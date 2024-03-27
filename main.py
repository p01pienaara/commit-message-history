


import argparse
import getcommits
import getUpdatedDependencies

def main(old_version, new_version):    
    if old_version is not None and new_version is not None:
        getUpdatedDependencies.purgeIfNeeded()
        getUpdatedDependencies.updateWithRange('git@github.com:discovery-ltd/v1-gutenberg-central-app-flutter.git', range=[new_version,old_version])
        getcommits.fetch()

    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="This script combines the commits messages from all changed dependencies in a modular Flutter app to easily see what changed from version to version")
    parser.add_argument("old_version", help="Provide the old and new version together to specify a version range to pull")
    parser.add_argument("new_version", help="Provide the old and new version together to specify a version range to pull")

    args = parser.parse_args()

    main(args.old_version, args.new_version)