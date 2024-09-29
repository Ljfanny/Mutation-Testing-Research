# Use the official Ubuntu 20.04 as the base image
FROM ubuntu:22.04

# Set environment variables to prevent prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Install necessary packages, JDK 17, and Python 3
RUN apt-get update && \
    apt-get install -y wget curl git openjdk-17-jdk python3 python3-pip && \
    apt-get clean

# Install Maven 3.8.1
RUN wget https://archive.apache.org/dist/maven/maven-3/3.8.1/binaries/apache-maven-3.8.1-bin.tar.gz -P /tmp && \
    tar xf /tmp/apache-maven-3.8.1-bin.tar.gz -C /opt && \
    ln -s /opt/apache-maven-3.8.1 /opt/maven && \
    ln -s /opt/maven/bin/mvn /usr/bin/mvn && \
    rm /tmp/apache-maven-3.8.1-bin.tar.gz

# Set environment variables for Maven
ENV MAVEN_HOME /opt/maven
ENV PATH $MAVEN_HOME/bin:$PATH

# Verify installations
RUN java -version && \
    mvn -version && \
    python3 --version && \
    pip3 --version

# Set the working directory
WORKDIR /app

# Define the default command to run when the container starts
CMD ["bash"]