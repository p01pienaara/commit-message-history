import getcommits
import getUpdatedDependencies

getUpdatedDependencies.update('git@github.com:discovery-ltd/v1-gutenberg-central-app-flutter.git', num_releases=10)
getcommits.fetch()