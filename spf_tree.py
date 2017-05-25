import subprocess
import json


class SPFNotFound(Exception):
    pass

class SPFTree:
    def __init__(self):
        self.results = None
        self.verbose = True
        self.dns_lookups = 0
        self.spf_stats = {
            "spf_length": 0,
            "include": set(),
            "exists": set(),
            "ip4": set(),
            "ip6": set(),
            "ptr": set(),
            "mx": set(),
            "a": set()
        }
        self.mechanisms = ["ip4", "ip6", "a", "mx", "ptr", "exists", "include"]

    @staticmethod
    def do_dig(domain, record_type):
        """
        Static helper method to do a dig for any domain and record type.
        :param domain: FQDN to lookup
        :param record_type: Any DNS type but TXT is used for all SPF lookups
        :return: list() of cleaned and concatenated TXT records for the domain
        """
        output = subprocess.check_output(["dig", "+short", "-t", record_type, domain]).decode()
        output = [x.strip().replace('" "', '').replace('"', "") for x in output.split("\n") if x != '']
        return output

    def parse_spf(self, domain):
        """
        The meat and sweet potatoes of the script. This actually parses the records and recursively follows includes
        while tracking the results locally and incrementing the metadata class object self.spf_stats
        :param domain: FQDN of the domain to lookup
        :return: returns a dict() object with the local data from each lookup as well as populates self.results with
        the information from the root lookup
        """
        # dig the domain and increment the DNS lookup counter for the class object
        dig_results = self.do_dig(domain, "TXT")
        self.dns_lookups += 1

        # Local variables for tracking data during recursion
        spf_raw = ""
        spf_record = []
        spf_stats = {
            "include": {},
            "exists": [],
            "fail": "",
            "ip4": [],
            "ip6": [],
            "ptr": [],
            "mx": [],
            "a": []
        }

        # Look for the spf record and store it
        for result in dig_results:
            if "v=spf" in result:
                spf_raw = result
                self.spf_stats["spf_length"] = len(spf_raw)
                spf_record = result.split(" ")
                break

        # Iter through the spf record and handle special cases first then dynamically process all mechanisms in the RFC
        for spf in spf_record:
            # Get the type and value if possible. These variables are used for dynamic processing later
            if "ip6" not in spf and ":" in spf:
                spf_type = spf.split(":")[0]
                spf_value = spf.split(":")[1]
            elif "ip6" in spf:
                # IPv6 messes with the splitting so it has to be split manually
                spf_type = "ip6"
                spf_value = spf.replace("ip6:", "")

            if "v=spf" in spf:
                # Ditch the useless version string
                pass
            elif "all" in spf:
                # Look for the all mechanism to see how the domain handles failures in lookups
                fail_mechanism = spf.replace("all", "")
                if len(fail_mechanism) > 0:
                    if fail_mechanism == "+":
                        spf_stats["fail"] = "Pass"
                    elif fail_mechanism == "-":
                        spf_stats["fail"] = "HardFail"
                    elif fail_mechanism == "~":
                        spf_stats["fail"] = "SoftFail"
                    elif fail_mechanism == "?":
                        spf_stats["fail"] = "Neutral"
                    else:
                        spf_stats["fail"] = "Unknown"
                else:
                    spf_stats["fail"] = "Unknown"
            elif "include:" in spf:
                # If it's an include statement recurse with another call to self.parse_spf()
                include_domain = spf.split(":")[1]
                if include_domain not in spf_stats["include"]:
                    if include_domain not in self.spf_stats["include"]:
                        self.spf_stats["include"].add(include_domain)
                        spf_stats["include"][include_domain] = self.parse_spf(include_domain)
            elif spf_type in self.mechanisms:
                # Dynamically handle all other mechanisms in the RFC
                if spf_value not in spf_stats[spf_type]:
                    if spf_value not in self.spf_stats[spf_type]:
                        self.spf_stats[spf_type].add(spf_value)
                    spf_stats[spf_type].append(spf_value)
                # All of the following types count against DNS lookup totals but don't really need a recursive check
                if spf_type in ["exists", "mx", "a", "ptr"]:
                    self.dns_lookups += 1

        # Populate the return object and set it for the class instance of self.results
        spf_result = {
            "domain": domain,
            "spf_text": spf_raw,
            "include": spf_stats["include"],
            "exists": spf_stats["exists"],
            "ip4": spf_stats["ip4"],
            "ip6": spf_stats["ip6"],
            "fail": spf_stats["fail"],
            "ptr": spf_stats["ptr"],
            "mx": spf_stats["mx"],
            "a": spf_stats["a"]
        }
        self.results = spf_result
        return self.results

    def print_spf_tree(self, leaf=None, depth=0):
        """
        Pretty prints out the root object from self.results and recurses through each lookup of an include increasing
        the depth for your visual pleasure. Dynamic and recursive.. ohhhh, shiny!
        :param leaf: Any given tier of a parse_spf() object
        :param depth: This is used to track the recursion depth and print out spaces/tabs accordingly
        :return:
        """
        # This is here so it can be called directly by a consumer of SPFTree() if necessary
        if not leaf:
            # If no leaf was passed in just grab the root object and go to town
            if self.results:
                leaf = self.results
            else:
                err_msg = "No leaf was passed in and no SPF record has been parsed yet. Use SPFTree.parse_spf()"
                raise SPFNotFound(err_msg)

        # If the depth is 0 it's the root object so we can print some banners and/or stats
        if depth == 0:
            print("{0} SPF Lookup Tree for {1} {0}".format("########", leaf["domain"]))
        print("|{}domain: {}".format("    " * depth, leaf["domain"]))

        # Iterate through the mechanisms for each leaf and print them out nice and formatted
        for mechanism in self.mechanisms:
            if len(leaf[mechanism]) > 0 and mechanism != "include":
                msg = "|{spacer}    | ---> {mechanism}: {values}"
                print(msg.format(spacer="    " * int(depth + 1), mechanism=mechanism, values=leaf[mechanism]))
            elif len(leaf[mechanism]) > 0 and mechanism == "include":
                # Includes need to recurse over the include object for proper depth tracking and printing
                print("|{}    | ---> includes: {}".format("    " * int(depth + 1),
                                                          [leaf["include"][x]["domain"] for x in
                                                           leaf["include"].keys()]))
                for include in leaf["include"]:
                    if leaf["include"][include] is not None:
                        self.print_spf_tree(leaf=leaf["include"][include], depth=int(depth + 2))

        # If it's the root object print out the stats for the domain
        if depth == 0:
            print("\nStats for {}:\n".format(leaf["domain"]),
                  "DNS Lookups:", self.dns_lookups, "\n",
                  "IPv4s:", len(self.spf_stats["ip4"]), "\n",
                  "IPv6s:", len(self.spf_stats["ip6"]), "\n",
                  "Fail type:", self.results["fail"]
                  )

    def spf_json(self):
        """
        Little helper method to return json if SPFTree is being consumed by a user and needed for actual useful tasks
        :return: json.dumps() string for the self.results root object
        """
        if self.results:
            return json.dumps(self.results)
        else:
            raise SPFNotFound("No results populated yet! Use SPFTree.parse_spf(domain)")



###### Using it #######
# Create the object
spf = SPFTree()

# Parse the domain
spf.parse_spf("somedomain.com")

# Pretty print that shit!
spf.print_spf_tree()
