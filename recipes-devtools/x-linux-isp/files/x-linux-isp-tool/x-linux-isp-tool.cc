/*
 * Copyright (c) 2024 STMicroelectronics.
 * All rights reserved.
 *
 * This software is licensed under terms that can be found in the LICENSE file
 * in the root directory of this software component.
 * If no LICENSE file comes with this software, it is provided AS-IS.
 *
 */

#include <iostream>
#include "readme.h"
#include <filesystem>
#include <stdio.h>
#include <getopt.h>
#include <fstream>
#include <string>
#include <vector>
#include <regex>
#include <array>
#include <cstdio>
#include <cstring>
#include <cstdlib>
#include <unordered_map>
#include <unordered_set>

/* Define global variables */
bool list = false;
bool to_remove = false;
bool to_install = false;
bool version = false;
bool features = false;

extern const std::string WIKI_LINK;
extern const std::string README_APPLI;
extern const std::string README_UTILITIES;
extern const std::string README_VERSION;
extern const std::string README_SOFTWARE;

struct packageInfo {
    std::string name;
    std::string version;
};

static void print_help(int argc, char** argv)
{
    std::cout <<
        "\nUsage:\t'" << argv[0] << " -[option]'\n"
        "\n"
        "-v --version            : Show X-LINUX-ISP current version if it is installed\n"
        "-f --supported-features : Print all supported frameworks in this X-LINUX-ISP version\n"
        "-l --list               : Print installed and ready-to-install packages\n"
        "-i --install <pkg>      : Install X-LINUX-ISP package\n"
        "-r --remove  <pkg>      : Remove X-LINUX-ISP package\n"
        "-h --help               : Show this help\n";
    exit(0);
}

void process_args(int argc, char** argv)
{
    const char* const short_opts = "i:r:vfhl";
    const option long_opts[] = {
        {"remove",   required_argument, nullptr, 'r'},
        {"install",  required_argument, nullptr, 'i'},
        {"supported-features",  no_argument, nullptr, 'f'},
        {"version",  no_argument, nullptr, 'v'},
        {"list",     no_argument, nullptr, 'l'},
        {"help",     no_argument, nullptr, 'h'},
        {nullptr,    no_argument, nullptr,  0 }
    };

    while (true)
    {
        const auto opt = getopt_long(argc, argv, short_opts, long_opts, nullptr);

        if (-1 == opt)
            break;
        switch (opt)
        {
        case 'v':
            version = true;
            break;
        case 'f':
            features = true;
            break;
        case 'l':
            list = true;
            break;
        case 'r':
            to_remove = true;
            break;
        case 'i':
            to_install = true;
            break;
        case 'h': // -h or --help
        case '?': // Unrecognized option
        default:
            print_help(argc, argv);
            break;
        }
    }
}

/* Get x-linux-isp pkgs list */
std::vector<packageInfo> _get_pkg(const std::string& file_path) {
    std::ifstream file(file_path);
    if (!file.is_open()) {
        std::cout << "\nTo install x-linux-isp packages, please follow the instructions provided on the wiki page: \n" + WIKI_LINK << std::endl;
        exit(1);
    }

    std::vector<packageInfo> pkgs;
    std::string line;
    packageInfo currentPackage;
    while (getline(file, line)) {
        if (line.find("Package: ") == 0 && line.find("x-linux-isp-tool") == std::string::npos) {
            currentPackage.name = line.substr(9); // Extract the package name
        } else if (line.find("Version: ") == 0) {
            currentPackage.version = line.substr(9); // Extract the version
        }

        if (!currentPackage.name.empty()) {
            pkgs.push_back(currentPackage);
        }
    }
    return pkgs;
}

std::tuple<std::vector<packageInfo>, std::vector<packageInfo>, std::vector<packageInfo>>
_sort_packages(const std::vector<packageInfo>& x_pkg, const std::vector<packageInfo>& ostl_pkg) {
    std::unordered_map<std::string, std::string> x_pkgMap;
    std::unordered_map<std::string, std::string> ostl_pkgMap;
    std::unordered_set<std::string> x_pkgNames;

    for (const auto& pkg : x_pkg) {
        x_pkgMap[pkg.name] = pkg.version;
        x_pkgNames.insert(pkg.name);
    }

    for (const auto& pkg : ostl_pkg) {
        ostl_pkgMap[pkg.name] = pkg.version;
    }

    std::vector<packageInfo> installedPackages;
    std::vector<packageInfo> upgradablePackages;
    std::vector<packageInfo> uninstalledPackages;

    for (const auto& name : x_pkgNames) {
        auto it1 = x_pkgMap.find(name);
        auto it2 = ostl_pkgMap.find(name);

        if (it1 != x_pkgMap.end() && it2 != ostl_pkgMap.end()) {
            if (it1->second == it2->second) {

                installedPackages.push_back({name, it1->second});
            } else {
                upgradablePackages.push_back({name, it1->second});
            }
        } else {
            if (it1 != x_pkgMap.end()) {
                uninstalledPackages.push_back({name, it1->second});
            }
        }
    }

    return std::make_tuple(installedPackages, upgradablePackages, uninstalledPackages);
}

bool _is_package_in_list(const std::vector<packageInfo>& packages, const std::string& packageName) {
    auto it = std::find_if(packages.begin(), packages.end(), [&packageName](const packageInfo& pkg) {
        return pkg.name == packageName;
    });
    return it != packages.end();
}

void print_pkgs(const std::vector<packageInfo>&  installedPackages,
                const std::vector<packageInfo>&  upgradablePackages,
                const std::vector<packageInfo>&  uninstalledPackages) {
    /* Installed packages */
    std::cout << "\n";
    for (const auto& pkg : installedPackages) {
        std::cout << " "
                  << "[installed]      "
                  << pkg.name
                  << std::endl;
    }

    /* Upgradable packages */
    std::cout << "\n";
    for (const auto& pkg : upgradablePackages) {
        std::cout << " "
                  << "[upgradable]     "
                  << pkg.name
                  << std::endl;
    }

    /* Ready-to-Install packages */
    std::cout << "\n";
    for (const auto& pkg : uninstalledPackages) {
        std::cout << " "
                  << "[not installed]  "
                  << pkg.name
                  << std::endl;
    }
    std::cout << "\n";
}

/* This function is used to install and uninstall pkgs */
void manage_pkgs(int argc, char** argv, bool install = true) {
    std::string command = (install ? "apt-get update && apt-get install -y " : "apt-get autoremove -y ") + std::string(argv[2]);
    int result = system(command.c_str());
    if (result == 0) {
        std::cout << std::string(argv[2])
                  << " has been "
                  << (install ? "installed" : "removed")
                  << " successfully."
                  << std::endl;
    } else {
        std::cout << "E: "
                  << "Failed to "
                  << (install ? "install" : "remove")
                  << " package "
                  << std::string(argv[2])
                  << std::endl;
        exit(1);
    }
}

std::string _get_x_pkg_path(const std::string& pattern, const std::vector<std::string>& directories) {
    std::regex regexPattern(pattern);

    for (const auto& dir : directories) {
        if (std::filesystem::exists(dir) && std::filesystem::is_directory(dir)) {
            for (const auto& entry : std::filesystem::directory_iterator(dir)) {
                if (entry.is_regular_file()) {
                    std::string filename = entry.path().filename().string();
                    if (std::regex_search(filename, regexPattern)) {
                        return entry.path().string();
                    }
                }
            }
        }
    }
    return "";
}

/// Main function ///
int main(int argc, char *argv[])
{
    process_args(argc, argv);

    if (version) {
        std::cout << "\nX-LINUX-ISP version: " << README_VERSION << "\n" << std::endl;
        return 0;
    }
    else if (features) {
        std::cout << "\nISP software:\n " << README_SOFTWARE << std::endl;
        std::cout << "\nApplication examples:\n " << README_APPLI << "\n" << std::endl;
        std::cout << "\nUtilities:\n " << README_UTILITIES << "\n" << std::endl;
        std::cout << "\nFind more information on the wiki page: https://wiki.st.com/stm32mpu/wiki/Category:X-LINUX-ISP_expansion_package" << std::endl;
        return 0;
    }

    /* Execute apt-get update first */
    FILE *fp;
    char path[1035];

    /* Open the command for reading */
    fp = popen("apt-get update 2>&1", "r");
    if (fp == NULL) {
        std::cout << "Fail to synchronize ISP packages, apt-get update fails." << std::endl;
        return 0;
    }

    /* Read the output a line at a time */
    while (fgets(path, sizeof(path) - 1, fp) != NULL) {
        /* Check for specific error message */
        if (strstr(path, "W: Failed") != NULL) {
            std::cout << "Fail to synchronize ISP packages, apt-get update fails." << std::endl;
            pclose(fp);
            return 0;
        }
    }

    /* Close the command stream */
    pclose(fp);


    /* Get list of ISP packages */
    /* 2 search paths to get the list of ISP packages: the official path and citool path */
    std::vector<std::string> directories = {
        "/var/lib/apt/lists/",
        "/var/lib/apt/lists/auxfiles/"
    };
    std::string pattern = ".*_ISP_.*_main_.*";

    std::string x_pkg_path = _get_x_pkg_path(pattern, directories);
    if (x_pkg_path.empty()) {
        std::cout << "list of ISP packages not found." << std::endl;
        return -1;
    }
    auto x_pkg = _get_pkg(x_pkg_path);

    /* Get ostl installed packages */
    std::string ostl_pkg_path = "/var/lib/dpkg/status";
    auto ostl_pkg = _get_pkg(ostl_pkg_path);

    /* Sort ISP packages in 3 categrories: installed, upgradable and not installed */
    auto [installedPackages, upgradablePackages, uninstalledPackages] = _sort_packages(x_pkg, ostl_pkg);

    if (list) {
        print_pkgs(installedPackages, upgradablePackages, uninstalledPackages);
    }
    else if (to_install && argc == 3) {
        manage_pkgs(argc, argv,true);
        /* If libcamera is not marked as installed then force the kernel module to be reloaded */
        if (!_is_package_in_list(installedPackages, "libcamera")) {
            std::cout << "\nKernel module stm32_dcmipp need to be reloaded: reload on going... " << std::endl;
            if (system("systemctl stop weston-graphical-session")) {
                std::cout << "Fail to upgrade the kernel module. Please reset your platform." << std::endl;
                return 0;
            }
            if (system("modprobe -r stm32_dcmipp")) {
                std::cout << "Fail to upgrade the kernel module. Please reset your platform." << std::endl;
                return 0;
            }
            std::cout << "\nWeston is restarting..." << std::endl;
            if (system("modprobe stm32_dcmipp")) {
                std::cout << "Fail to upgrade the kernel module. Please reset your platform." << std::endl;
                return 0;
            }
            if (system("systemctl start weston-graphical-session")) {
                std::cout << "Fail to upgrade the kernel module. Please reset your platform." << std::endl;
                return 0;
            }
            std::cout << "\nKernel module stm32_dcmipp reload successfully done." << std::endl;
        }
    }
    else if (to_remove && argc == 3) {
        manage_pkgs(argc, argv,false);
    }
    else{
        print_help(argc, argv);
    }
    return 0;
}
