#!/bin/bash
REPO_URL=$1
COMMIT_CODE=$2
SUBDIR=${10}
GUIDING_FILE_URL="https://www.dropbox.com/scl/fi/nzuj3v37n2mt6ccl407tn/guiding_file.tar?rlkey=zwy2ge5pk1ojzj3878nq12wf3&st=11eipoie&dl=0"
# GUIDING_FILE_URL="https://www.dropbox.com/scl/fi/0olayskeytpmx3m7ppg87/delight-nashorn-sandbox.json?rlkey=9wv4erxuxrwzw67n9xcxq6ljr&st=x8n0dwa0&dl=0"
GUIDING_FILE_NAME="guiding_file.tar"
# GUIDING_FILE_NAME="delight-nashorn-sandbox.json"
PITest_URL="https://github.com/UT-SE-Research/pitest-random.git"
REPO_NAME=$(basename "$REPO_URL" .git)
REPO_PATH="/jl85223/mutation-testing-research/controlled-projects/$SUBDIR/$REPO_NAME"

wget $GUIDING_FILE_URL -O $GUIDING_FILE_NAME
tar -xvf $GUIDING_FILE_NAME
git clone $PITest_URL
mv guiding_file pitest-random/pitest/src/main/resources/
# mv $GUIDING_FILE_NAME pitest-random/pitest/src/main/resources/
cd pitest-random
git switch jiefang
mvn install -DskipTests
cd ../

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
readFromFile=$7
filePath=$8
round="${9:-5}" #number to run pitest, default is 5

for (( i=0; i<$round; i++ ))
do
    echo "Start $i time running PITest"
    mvn test-compile org.pitest:pitest-maven:mutationCoverage -Dmaven.ext.class.path=/jl85223/mutation-testing-research/pitest-injector-1.0.jar -DrandomMutant=$randomMutant -DrandomTest=$randomTest -Dverbosity=$verbosity -DrandomSeed=$randomSeed -DreadFromFile=$readFromFile -DfilePath=$filePath > "/jl85223/mutation-testing-research/controlled-logs/$SUBDIR/${REPO_NAME}_$i.log" 2>&1
    cp -r . "${REPO_PATH}_$i"
    mvn clean
done