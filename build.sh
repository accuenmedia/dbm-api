
#!/bin/bash
set -eu -o pipefail

export BUILD_CONTEXT=$(pwd)
export DOCKER_BUILDKIT=1
export AWS_DEFAULT_REGION=us-west-2
export BUILD_ENV="$1"

ECR="348194362585.dkr.ecr.us-west-2.amazonaws.com"
REPOSITORY_NAME="changeme"
VERSION="0.0.1"
[[ -z ${BUILDKITE_BUILD_NUMBER+x} ]] && NUMBER="0" || NUMBER="${BUILDKITE_BUILD_NUMBER}"
[[ -z ${BUILDKITE_COMMIT+x} ]] && COMMIT=$(git rev-parse --short HEAD) || COMMIT="${BUILDKITE_COMMIT}"
[[ -z ${BUILDKITE_BRANCH+x} ]] && BRANCH=$(git rev-parse --abbrev-ref HEAD) || BRANCH="${BUILDKITE_BRANCH}"

echo "--- :aws: :ecr: aws ecr docker login"
ecr_passwd=$(aws ecr get-login-password --region $AWS_DEFAULT_REGION)
echo "$ecr_passwd" | docker login -u AWS --password-stdin "$ECR"

ecrrepo="$ECR/$REPOSITORY_NAME"
tags=($ecrrepo:c-$COMMIT $ecrrepo:b-$BRANCH $ecrrepo:n-$NUMBER $ecrrepo:v-$VERSION $ecrrepo:latest)

docker_build() {
  docker build --ssh default --progress plain -t package -f Dockerfile     --label commit=$COMMIT     --label branch=$BRANCH     --label number=$NUMBER     --label version=$VERSION     --build-arg COMMIT=$COMMIT     --build-arg BRANCH=$BRANCH     --build-arg NUMBER=$NUMBER     --build-arg VERSION=$VERSION     .

  for t in ${tags[*]}
  do
      echo "tagging package as ${t}"
      docker tag package ${t}
      docker push ${t}
  done
}

echo "--- :docker: docker build"
echo "docker build for $BUILD_ENV"
## docker_build
