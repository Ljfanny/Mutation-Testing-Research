#!/bin/bash
REPO_URL=$1
COMMIT_CODE=$2
SUBDIR=$8
PITest_URL="https://github.com/UT-SE-Research/pitest-random.git"
REPO_NAME=$(basename "$REPO_URL" .git)
REPO_PATH="/jl85223/mutation-testing-research/pitest-projects/$SUBDIR/$REPO_NAME"

git clone $PITest_URL
cd pitest-random && mvn install -DskipTests

git clone $REPO_URL
cd $REPO_NAME
git checkout $COMMIT_CODE

if [ -f pom.xml ]; then
    echo "pom.xml exists."
else
    echo "pom.xml does not exist."
    exit 1
fi

randomMutant=$3 #true or false
randomTest=$4 #true or false
verbosity=$5 #RANDOM_VERBOSE or default
randomSeed=$6 #a random number
round="${7:-5}" #number to run pitest, default is 5

for (( i=0; i<=$round; i++ ))
do
    echo "Start $i time running PITest"
    mvn test-compile org.pitest:pitest-maven:mutationCoverage -Dmaven.ext.class.path=/jl85223/mutation-testing-research/pitest-injector-1.0.jar -DrandomMutant=$randomMutant -DrandomTest=$randomTest -Dverbosity=$verbosity -DrandomSeed=$randomSeed > "/jl85223/mutation-testing-research/pitest-logs/$SUBDIR/${REPO_NAME}_$i.log" 2>&1
    cp -r . "${REPO_PATH}_$i"
    mvn clean
done