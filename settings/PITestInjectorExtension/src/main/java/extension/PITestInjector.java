package extension;

import javax.inject.Named;
import javax.inject.Singleton;

import org.apache.maven.AbstractMavenLifecycleParticipant;
import org.apache.maven.execution.MavenSession;
import org.apache.maven.model.Build;
import org.apache.maven.model.Model;
import org.apache.maven.model.Plugin;
import org.apache.maven.model.PluginExecution;
import org.apache.maven.model.PluginManagement;
import org.apache.maven.model.Dependency;
import org.apache.maven.project.MavenProject;
import org.codehaus.plexus.util.xml.Xpp3Dom;
import java.util.List;

@Named("PITest-Injector")
@Singleton
public class PITestInjector extends AbstractMavenLifecycleParticipant {
    @Override
    public void afterProjectsRead(MavenSession session) {
        System.out.println("AfterProjectsRead");
        for (MavenProject project : session.getProjects()) {

            Model model = project.getModel();
            Build build = model.getBuild();

            if (build == null) {
                build = new Build();
                model.setBuild(build);
            }

            // Get the Java version set in the Maven project, default to "17"
            // String compilerPluginVersion = "3.10.1";
            // String javaSource = model.getProperties().getProperty("maven.compiler.source", "17");
            // String javaTarget = model.getProperties().getProperty("maven.compiler.target", "17");

            // Get the Java version set in the Maven project, default to "8"
            String compilerPluginVersion = "3.8.1";
            String javaSource = model.getProperties().getProperty("maven.compiler.source", "1.8");
            String javaTarget = model.getProperties().getProperty("maven.compiler.target", "1.8");

            // If maven.compiler.target is not set, default to the same version as source
            if (javaTarget == null || javaTarget.isEmpty()) {
                javaTarget = javaSource;
            }

            // Check if maven-compiler-plugin exists in <plugins>
            Plugin compilerPlugin_1 = null;
            List<Plugin> plugins_1 = build.getPlugins();
            for (Plugin plugin : plugins_1) {
                if ("org.apache.maven.plugins".equals(plugin.getGroupId()) && "maven-compiler-plugin".equals(plugin.getArtifactId())) {
                    compilerPlugin_1 = plugin;
                    break;
                }
            }

            // If it doesn't exist, create a new maven-compiler-plugin
            if (compilerPlugin_1 == null) {
                compilerPlugin_1 = new Plugin();
                compilerPlugin_1.setGroupId("org.apache.maven.plugins");
                compilerPlugin_1.setArtifactId("maven-compiler-plugin");
                compilerPlugin_1.setVersion(compilerPluginVersion); // Update to a version that supports Java 17
                build.addPlugin(compilerPlugin_1);
            }

            // Modify the source and target of maven-compiler-plugin
            for (PluginExecution execution : compilerPlugin_1.getExecutions()) { 
                Xpp3Dom execConfiguration_1 = (Xpp3Dom) execution.getConfiguration();
                if (execConfiguration_1 == null) {
                    execConfiguration_1 = new Xpp3Dom("configuration");
                    execution.setConfiguration(execConfiguration_1);
                }

                // Set the source version
                Xpp3Dom execSource_1 = execConfiguration_1.getChild("source");
                if (execSource_1 == null) {
                    execSource_1 = new Xpp3Dom("source");
                    execConfiguration_1.addChild(execSource_1);
                }
                execSource_1.setValue(javaSource);

                // Set the target version
                Xpp3Dom execTarget_1 = execConfiguration_1.getChild("target");
                if (execTarget_1 == null) {
                    execTarget_1 = new Xpp3Dom("target");
                    execConfiguration_1.addChild(execTarget_1);
                }
                execTarget_1.setValue(javaTarget);
            }

            // Check if maven-compiler-plugin exists in <pluginManagement>
            PluginManagement pluginManagement = build.getPluginManagement();
            if (pluginManagement != null) {
                List<Plugin> plugins_2 = pluginManagement.getPlugins();
                Plugin compilerPlugin_2 = null;
                for (Plugin plugin : plugins_2) {
                    if ("org.apache.maven.plugins".equals(plugin.getGroupId()) && "maven-compiler-plugin".equals(plugin.getArtifactId())) {
                        compilerPlugin_2 = plugin;
                        break;
                    }
                }

                // Modify the source and target of maven-compiler-plugin
                if (compilerPlugin_2 != null) {
                    compilerPlugin_2.setVersion(compilerPluginVersion); // Update to a version that supports Java 17
                    for (PluginExecution execution : compilerPlugin_2.getExecutions()) { 
                        Xpp3Dom execConfiguration_2 = (Xpp3Dom) execution.getConfiguration();
                        if (execConfiguration_2 == null) {
                            execConfiguration_2 = new Xpp3Dom("configuration");
                            execution.setConfiguration(execConfiguration_2);
                        }

                        // Set the source version
                        Xpp3Dom execSource_2 = execConfiguration_2.getChild("source");
                        if (execSource_2 == null) {
                            execSource_2 = new Xpp3Dom("source");
                            execConfiguration_2.addChild(execSource_2);
                        }
                        execSource_2.setValue(javaSource);

                        // Set the target version
                        Xpp3Dom execTarget_2 = execConfiguration_2.getChild("target");
                        if (execTarget_2 == null) {
                            execTarget_2 = new Xpp3Dom("target");
                            execConfiguration_2.addChild(execTarget_2);
                        }
                        execTarget_2.setValue(javaTarget);
                    }
                }
            }

            // Insert the pitest plugin
            Plugin pitestPlugin = new Plugin();
            pitestPlugin.setGroupId("org.pitest");
            pitestPlugin.setArtifactId("pitest-maven");
            pitestPlugin.setVersion("dev-random-SNAPSHOT");

            PluginExecution pitestExecution = new PluginExecution();
            pitestExecution.addGoal("mutationCoverage");
            pitestPlugin.addExecution(pitestExecution);

            Xpp3Dom configuration = new Xpp3Dom("configuration");
            Xpp3Dom outputFormats = new Xpp3Dom("outputFormats");
            Xpp3Dom outputFormat = new Xpp3Dom("outputFormat");
            outputFormat.setValue("XML");
            outputFormats.addChild(outputFormat);
            configuration.addChild(outputFormats);

            // Xpp3Dom skipFailingTests = new Xpp3Dom("skipFailingTests");
            // skipFailingTests.setValue("true");
            // configuration.addChild(skipFailingTests);

            Xpp3Dom fullMutationMatrix = new Xpp3Dom("fullMutationMatrix");
            fullMutationMatrix.setValue("true");
            configuration.addChild(fullMutationMatrix);

            Xpp3Dom exportLineCoverage = new Xpp3Dom("exportLineCoverage");
            exportLineCoverage.setValue("true");
            configuration.addChild(exportLineCoverage);

            // Set default configuration values
            String randomMutantValue = System.getProperty("randomMutant", "false");
            String randomTestValue = System.getProperty("randomTest", "false");
            String verbosityValue = System.getProperty("verbosity", "default");
            String randomSeedValue = System.getProperty("randomSeed", "99999");

            Xpp3Dom randomMutant = new Xpp3Dom("randomMutant");
            randomMutant.setValue(randomMutantValue);
            configuration.addChild(randomMutant);

            Xpp3Dom randomTest = new Xpp3Dom("randomTest");
            randomTest.setValue(randomTestValue);
            configuration.addChild(randomTest);

            Xpp3Dom verbosity = new Xpp3Dom("verbosity");
            verbosity.setValue(verbosityValue);
            configuration.addChild(verbosity);

            Xpp3Dom randomSeed = new Xpp3Dom("randomSeed");
            randomSeed.setValue(randomSeedValue);
            configuration.addChild(randomSeed);

            pitestPlugin.setConfiguration(configuration);

            // Add pitest-junit5-plugin dependency
            for (Dependency tmp_dependency : project.getDependencies()) { 
                if ("org.junit.jupiter".equals(tmp_dependency.getGroupId())) {
                    org.apache.maven.model.Dependency dependency = new org.apache.maven.model.Dependency();
                    dependency.setGroupId("org.pitest");
                    dependency.setArtifactId("pitest-junit5-plugin");
                    dependency.setVersion("1.2.1");
                    pitestPlugin.addDependency(dependency);
                    break;
                }
            }

            build.addPlugin(pitestPlugin);           
        }
    }
}