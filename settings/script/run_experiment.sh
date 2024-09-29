#!/bin/bash
IMAGE_NAME="pitest"
ROOT_PATH="/jl85223/mutation-testing-research"
DOCKERFILE_PATH="~/$ROOT_PATH/running-setup/Dockerfile" 
RUN_PITEST_PATH="$ROOT_PATH/running-setup/script/run_pitest.sh"
DOCKER_BUILD_CONTEXT="."

if docker image inspect "$IMAGE_NAME" &> /dev/null; then
    echo "Docker image '$IMAGE_NAME' already exists. Skipping build."
else
    echo "Docker image '$IMAGE_NAME' does not exist. Building..."
    docker build -t "$IMAGE_NAME" -f "$DOCKERFILE_PATH" "$DOCKER_BUILD_CONTEXT"
    BUILD_SUCCESS=$?
    if [ $BUILD_SUCCESS -ne 0 ]; then
        echo "Failed to build Docker image."
        exit 1
    fi
    echo "Docker image '$IMAGE_NAME' built successfully."
fi

echo "Creating Docker container from image '$IMAGE_NAME'..."
CONTAINER_ID=$(docker run -d -it -v /home/hy7595/jl85223:/jl85223 "$IMAGE_NAME")
CREATE_SUCCESS=$?
if [ $CREATE_SUCCESS -ne 0 ]; then
    echo "Failed to create Docker container."
    exit 1
fi
echo "Docker container created successfully."

REPO_URL=$1
COMMIT_CODE=$2
randomMutant=$3 #true or false
randomTest=$4 #true or false
verbosity=$5 #RANDOM_VERBOSE or default
randomSeed=$6 #a random number
round="${7:-5}" #number to run pitest, default is 5

if [[ "$randomMutant" == "true" && "$randomTest" == "false" ]]; then
    SUBDIR="random-mutant_default-test/$randomSeed"
elif [[ "$randomMutant" == "false" && "$randomTest" == "true" ]]; then
    SUBDIR="default-mutant_random-test/$randomSeed"
elif [[ "$randomMutant" == "true" && "$randomTest" == "true" ]]; then
    SUBDIR="random-mutant_random-test/$randomSeed"
fi

docker exec -it "$CONTAINER_ID" /bin/bash -c "chmod +x $RUN_PITEST_PATH && $RUN_PITEST_PATH $REPO_URL $COMMIT_CODE $randomMutant $randomTest $verbosity $randomSeed $round $SUBDIR"
docker stop $CONTAINER_ID
docker rm $CONTAINER_ID