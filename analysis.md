## delight-nashorn-sandbox

WRONG!!! It is flaky, I tried the same thing again, it is killed. So it is inherently flaky.

## jimfs

com.google.common.jimfs.FileTree.$assertionsDisabled ???

```
[no impacted]
com.google.common.jimfs.ConfigurationTest.testFileSystemForCustomConfiguration
com.google.common.jimfs.JimfsWindowsLikeFileSystemTest.testPaths_toRealPath
com.google.common.jimfs.JimfsWindowsLikeFileSystemTest.testPaths_toUri

[in the same mutant]
com.google.common.jimfs.ConfigurationTest.testFileSystemForDefaultUnixConfiguration
[ERROR-No mutations found]
com.google.common.jimfs.ConfigurationTest.testFileSystemForDefaultWindowsConfiguration

[ERROR-No mutations found]
com.google.common.jimfs.JimfsUnixLikeFileSystemTest.testDelete_pathPermutations
com.google.common.jimfs.JimfsUnixLikeFileSystemTest.testSecureDirectoryStream

[no exist]
com.google.common.jimfs.FileTreeTest.testLookup_absolute_withDotDotsInPath
com.google.common.jimfs.FileTreeTest.testLookup_absolute_withDotDotsInPath_afterSymlink
com.google.common.jimfs.FileTreeTest.testLookup_absolute_withDotsInPath
com.google.common.jimfs.FileTreeTest.testLookup_relative_emptyPath
com.google.common.jimfs.FileTreeTest.testLookup_relative_withDotDotsInPath
com.google.common.jimfs.FileTreeTest.testLookup_relative_withDotDotsInPath_afterSymlink
com.google.common.jimfs.FileTreeTest.testLookup_relative_withDotsInPath
com.google.common.jimfs.JimfsUnixLikeFileSystemTest.testDelete_directory_canDeleteWorkingDirectoryByAbsolutePath
com.google.common.jimfs.JimfsUnixLikeFileSystemTest.testDelete_directory_cantDeleteRoot
com.google.common.jimfs.JimfsUnixLikeFileSystemTest.testDelete_directory_cantDeleteWorkingDirectoryByRelativePath
com.google.common.jimfs.JimfsUnixLikeFileSystemTest.testPathLookups
com.google.common.jimfs.JimfsUnixLikeFileSystemTest.testPaths_toRealPath
com.google.common.jimfs.JimfsUnixLikeFileSystemTest.testPaths_toUri
com.google.common.jimfs.WatchServiceConfigurationTest.testDefaultConfig
```

com.google.common.jimfs.ConfigurationTest.testFileSystemForDefaultOsXConfiguration:

```java
@Test
public void testFileSystemForDefaultOsXConfiguration() throws IOException {
    FileSystem fs = Jimfs.newFileSystem(Configuration.osX());

    assertThat(fs.getRootDirectories())
        .containsExactlyElementsIn(ImmutableList.of(fs.getPath("/")))
        .inOrder();
    assertThatPath(fs.getPath("").toRealPath()).isEqualTo(fs.getPath("/work"));
    assertThat(Iterables.getOnlyElement(fs.getFileStores()).getTotalSpace())
        .isEqualTo(4L * 1024 * 1024 * 1024);
    assertThat(fs.supportedFileAttributeViews()).containsExactly("basic");

    Files.createFile(fs.getPath("/foo"));

    try {
      Files.createFile(fs.getPath("/FOO"));
      fail();
    } catch (FileAlreadyExistsException expected) {
    }
}
```

### 592 (0) -- Unknown

The mutant that this pair comes from is not always found. It depends on other mutants.

Run 0-jimfs_6-0-edge_5-0-mid.json, both fail.

Run 0-jimfs_6-0-edge_5-0-mid_dummy.json (polluted mutant did nothing), only polluter exists and passes.

#### polluter

##### code

```java
// Configuration.java
@CanIgnoreReturnValue
public Builder setNameCanonicalNormalization(PathNormalization first, PathNormalization... more) {
    this.nameCanonicalNormalization = checkNormalizations(Lists.asList(first, more));
    return this; // return null
}
```

```java
// ConfigurationTest.java
@Test
public void testDefaultOsXConfiguration() {
    Configuration config = Configuration.osX();

    assertThat(config.pathType).isEqualTo(PathType.unix());
    assertThat(config.roots).containsExactly("/");
    assertThat(config.workingDirectory).isEqualTo("/work");
    assertThat(config.nameCanonicalNormalization).containsExactly(NFD, CASE_FOLD_ASCII);
    assertThat(config.nameDisplayNormalization).containsExactly(NFC);
    assertThat(config.pathEqualityUsesCanonicalForm).isFalse();
    assertThat(config.blockSize).isEqualTo(8192);
    assertThat(config.maxSize).isEqualTo(4L * 1024 * 1024 * 1024);
    assertThat(config.maxCacheSize).isEqualTo(-1);
    assertThat(config.attributeViews).containsExactly("basic");
    assertThat(config.attributeProviders).isEmpty();
    assertThat(config.defaultAttributeValues).isEmpty();
    assertThat(config.fileTimeSource).isEqualTo(SystemFileTimeSource.INSTANCE);
}
```

##### results

```
mvn test -Dtest=ConfigurationTest#testDefaultOsXConfiguration

[INFO] -------------------------------------------------------
[INFO]  T E S T S
[INFO] -------------------------------------------------------
[INFO] Running com.google.common.jimfs.ConfigurationTest
[ERROR] Tests run: 1, Failures: 0, Errors: 1, Skipped: 0, Time elapsed: 0.052 s <<< FAILURE! -- in com.google.common.jimfs.ConfigurationTest
[ERROR] com.google.common.jimfs.ConfigurationTest.testDefaultOsXConfiguration -- Time elapsed: 0.021 s <<< ERROR!
java.lang.ExceptionInInitializerError
        at com.google.common.jimfs.Configuration.osX(Configuration.java:134)
        at com.google.common.jimfs.ConfigurationTest.testDefaultOsXConfiguration(ConfigurationTest.java:94)
        at java.base/jdk.internal.reflect.NativeMethodAccessorImpl.invoke0(Native Method)
        at java.base/jdk.internal.reflect.NativeMethodAccessorImpl.invoke(NativeMethodAccessorImpl.java:77)
        at java.base/jdk.internal.reflect.DelegatingMethodAccessorImpl.invoke(DelegatingMethodAccessorImpl.java:43)
        at java.base/java.lang.reflect.Method.invoke(Method.java:569)
        at org.junit.runners.model.FrameworkMethod$1.runReflectiveCall(FrameworkMethod.java:59)
        at org.junit.internal.runners.model.ReflectiveCallable.run(ReflectiveCallable.java:12)
        at org.junit.runners.model.FrameworkMethod.invokeExplosively(FrameworkMethod.java:56)
        at org.junit.internal.runners.statements.InvokeMethod.evaluate(InvokeMethod.java:17)
        at org.junit.runners.ParentRunner$3.evaluate(ParentRunner.java:306)
        at org.junit.runners.BlockJUnit4ClassRunner$1.evaluate(BlockJUnit4ClassRunner.java:100)
        at org.junit.runners.ParentRunner.runLeaf(ParentRunner.java:366)
        at org.junit.runners.BlockJUnit4ClassRunner.runChild(BlockJUnit4ClassRunner.java:103)
        at org.junit.runners.BlockJUnit4ClassRunner.runChild(BlockJUnit4ClassRunner.java:63)
        at org.junit.runners.ParentRunner$4.run(ParentRunner.java:331)
        at org.junit.runners.ParentRunner$1.schedule(ParentRunner.java:79)
        at org.junit.runners.ParentRunner.runChildren(ParentRunner.java:329)
        at org.junit.runners.ParentRunner.access$100(ParentRunner.java:66)
        at org.junit.runners.ParentRunner$2.evaluate(ParentRunner.java:293)
        at org.junit.runners.ParentRunner$3.evaluate(ParentRunner.java:306)
        at org.junit.runners.ParentRunner.run(ParentRunner.java:413)
        at org.apache.maven.surefire.junit4.JUnit4Provider.execute(JUnit4Provider.java:316)
        at org.apache.maven.surefire.junit4.JUnit4Provider.executeWithRerun(JUnit4Provider.java:240)
        at org.apache.maven.surefire.junit4.JUnit4Provider.executeTestSet(JUnit4Provider.java:214)
        at org.apache.maven.surefire.junit4.JUnit4Provider.invoke(JUnit4Provider.java:155)
        at org.apache.maven.surefire.booter.ForkedBooter.runSuitesInProcess(ForkedBooter.java:385)
        at org.apache.maven.surefire.booter.ForkedBooter.execute(ForkedBooter.java:162)
        at org.apache.maven.surefire.booter.ForkedBooter.run(ForkedBooter.java:507)
        at org.apache.maven.surefire.booter.ForkedBooter.main(ForkedBooter.java:495)
Caused by: java.lang.NullPointerException: Cannot invoke "com.google.common.jimfs.Configuration$Builder.setSupportedFeatures(com.google.common.jimfs.Feature[])" because the return value of "com.google.common.jimfs.Configuration$Builder.setNameCanonicalNormalization(com.google.common.jimfs.PathNormalization, com.google.common.jimfs.PathNormalization[])" is null
        at com.google.common.jimfs.Configuration$OsxHolder.<clinit>(Configuration.java:143)
        ... 30 more

[INFO] 
[INFO] Results:
[INFO] 
[ERROR] Errors: 
[ERROR]   ConfigurationTest.testDefaultOsXConfiguration:94 ? ExceptionInInitializer
[INFO] 
[ERROR] Tests run: 1, Failures: 0, Errors: 1, Skipped: 0
[INFO] 
[INFO] ------------------------------------------------------------------------
```

```
mvn test -Dtest=ConfigurationTest#testFileSystemForDefaultOsXConfiguration

[INFO] -------------------------------------------------------
[INFO]  T E S T S
[INFO] -------------------------------------------------------
[INFO] Running com.google.common.jimfs.ConfigurationTest
[ERROR] Tests run: 1, Failures: 0, Errors: 1, Skipped: 0, Time elapsed: 0.054 s <<< FAILURE! -- in com.google.common.jimfs.ConfigurationTest
[ERROR] com.google.common.jimfs.ConfigurationTest.testFileSystemForDefaultOsXConfiguration -- Time elapsed: 0.020 s <<< ERROR!
java.lang.ExceptionInInitializerError
        at com.google.common.jimfs.Configuration.osX(Configuration.java:134)
        at com.google.common.jimfs.ConfigurationTest.testFileSystemForDefaultOsXConfiguration(ConfigurationTest.java:113)
        at java.base/jdk.internal.reflect.NativeMethodAccessorImpl.invoke0(Native Method)
        at java.base/jdk.internal.reflect.NativeMethodAccessorImpl.invoke(NativeMethodAccessorImpl.java:77)
        at java.base/jdk.internal.reflect.DelegatingMethodAccessorImpl.invoke(DelegatingMethodAccessorImpl.java:43)
        at java.base/java.lang.reflect.Method.invoke(Method.java:569)
        at org.junit.runners.model.FrameworkMethod$1.runReflectiveCall(FrameworkMethod.java:59)
        at org.junit.internal.runners.model.ReflectiveCallable.run(ReflectiveCallable.java:12)
        at org.junit.runners.model.FrameworkMethod.invokeExplosively(FrameworkMethod.java:56)
        at org.junit.internal.runners.statements.InvokeMethod.evaluate(InvokeMethod.java:17)
        at org.junit.runners.ParentRunner$3.evaluate(ParentRunner.java:306)
        at org.junit.runners.BlockJUnit4ClassRunner$1.evaluate(BlockJUnit4ClassRunner.java:100)
        at org.junit.runners.ParentRunner.runLeaf(ParentRunner.java:366)
        at org.junit.runners.BlockJUnit4ClassRunner.runChild(BlockJUnit4ClassRunner.java:103)
        at org.junit.runners.BlockJUnit4ClassRunner.runChild(BlockJUnit4ClassRunner.java:63)
        at org.junit.runners.ParentRunner$4.run(ParentRunner.java:331)
        at org.junit.runners.ParentRunner$1.schedule(ParentRunner.java:79)
        at org.junit.runners.ParentRunner.runChildren(ParentRunner.java:329)
        at org.junit.runners.ParentRunner.access$100(ParentRunner.java:66)
        at org.junit.runners.ParentRunner$2.evaluate(ParentRunner.java:293)
        at org.junit.runners.ParentRunner$3.evaluate(ParentRunner.java:306)
        at org.junit.runners.ParentRunner.run(ParentRunner.java:413)
        at org.apache.maven.surefire.junit4.JUnit4Provider.execute(JUnit4Provider.java:316)
        at org.apache.maven.surefire.junit4.JUnit4Provider.executeWithRerun(JUnit4Provider.java:240)
        at org.apache.maven.surefire.junit4.JUnit4Provider.executeTestSet(JUnit4Provider.java:214)
        at org.apache.maven.surefire.junit4.JUnit4Provider.invoke(JUnit4Provider.java:155)
        at org.apache.maven.surefire.booter.ForkedBooter.runSuitesInProcess(ForkedBooter.java:385)
        at org.apache.maven.surefire.booter.ForkedBooter.execute(ForkedBooter.java:162)
        at org.apache.maven.surefire.booter.ForkedBooter.run(ForkedBooter.java:507)
        at org.apache.maven.surefire.booter.ForkedBooter.main(ForkedBooter.java:495)
Caused by: java.lang.NullPointerException: Cannot invoke "com.google.common.jimfs.Configuration$Builder.setSupportedFeatures(com.google.common.jimfs.Feature[])" because the return value of "com.google.common.jimfs.Configuration$Builder.setNameCanonicalNormalization(com.google.common.jimfs.PathNormalization, com.google.common.jimfs.PathNormalization[])" is null
        at com.google.common.jimfs.Configuration$OsxHolder.<clinit>(Configuration.java:143)
        ... 30 more

[INFO] 
[INFO] Results:
[INFO] 
[ERROR] Errors: 
[ERROR]   ConfigurationTest.testFileSystemForDefaultOsXConfiguration:113 ? ExceptionInInitializer
[INFO] 
[ERROR] Tests run: 1, Failures: 0, Errors: 1, Skipped: 0
[INFO] 
[INFO] ------------------------------------------------------------------------
```

#### victim

##### code

```java
// JimfsFileChannel.java
@Override
protected void implCloseChannel() {
    try {
        synchronized (blockingThreads) {
            for (Thread thread : blockingThreads) {
                thread.interrupt();
            }
        }
    } finally {
        fileSystemState.unregister(this); // remove call
        file.closed();
    }
}
```

##### results

```
mvn test -Dtest=ConfigurationTest#testDefaultOsXConfiguration

[INFO] -------------------------------------------------------
[INFO]  T E S T S
[INFO] -------------------------------------------------------
[INFO] Running com.google.common.jimfs.ConfigurationTest
[INFO] Tests run: 1, Failures: 0, Errors: 0, Skipped: 0, Time elapsed: 0.060 s -- in com.google.common.jimfs.ConfigurationTest
[INFO] 
[INFO] Results:
[INFO] 
[INFO] Tests run: 1, Failures: 0, Errors: 0, Skipped: 0
[INFO] 
[INFO] ------------------------------------------------------------------------
```

```
mvn test -Dtest=ConfigurationTest#testFileSystemForDefaultOsXConfiguration

[INFO] -------------------------------------------------------
[INFO]  T E S T S
[INFO] -------------------------------------------------------
[INFO] Running com.google.common.jimfs.ConfigurationTest
[INFO] Tests run: 1, Failures: 0, Errors: 0, Skipped: 0, Time elapsed: 0.093 s -- in com.google.common.jimfs.ConfigurationTest
[INFO] 
[INFO] Results:
[INFO] 
[INFO] Tests run: 1, Failures: 0, Errors: 0, Skipped: 0
[INFO] 
[INFO] ------------------------------------------------------------------------
```

### 656 (1) -- Unknown

The mutant that this pair comes from is not always found. It depends on other mutants.

Run 1-jimfs_6-0-edge_5-0-mid.json, both fail.

Run 1-jimfs_6-0-edge_5-0-mid_dummy.json (polluted mutant did nothing), only polluter exists and passes.

#### polluter

The same as 592.

#### victim

##### code

```java
// JimfsFileChannel.java
@Override
protected void implCloseChannel() {
    try {
        synchronized (blockingThreads) {
            for (Thread thread : blockingThreads) {
                thread.interrupt();
            }
        }
    } finally {
        fileSystemState.unregister(this);
        file.closed(); // remove call
    }
}
```

##### results

```
mvn test -Dtest=ConfigurationTest#testDefaultOsXConfiguration

[INFO] -------------------------------------------------------
[INFO]  T E S T S
[INFO] -------------------------------------------------------
[INFO] Running com.google.common.jimfs.ConfigurationTest
[INFO] Tests run: 1, Failures: 0, Errors: 0, Skipped: 0, Time elapsed: 0.061 s -- in com.google.common.jimfs.ConfigurationTest
[INFO] 
[INFO] Results:
[INFO] 
[INFO] Tests run: 1, Failures: 0, Errors: 0, Skipped: 0
[INFO] 
[INFO] ------------------------------------------------------------------------
```

```
mvn test -Dtest=ConfigurationTest#testFileSystemForDefaultOsXConfiguration

[INFO] -------------------------------------------------------
[INFO]  T E S T S
[INFO] -------------------------------------------------------
[INFO] Running com.google.common.jimfs.ConfigurationTest
[INFO] Tests run: 1, Failures: 0, Errors: 0, Skipped: 0, Time elapsed: 0.103 s -- in com.google.common.jimfs.ConfigurationTest
[INFO] 
[INFO] Results:
[INFO] 
[INFO] Tests run: 1, Failures: 0, Errors: 0, Skipped: 0
[INFO] 
[INFO] ------------------------------------------------------------------------
```

### 3317 (2) -- Survived

Run 2-jimfs_5-0-mid_9-0-mid.json, both fail.

Run 2-jimfs_5-0-mid_9-0-mid_dummy.json (polluted mutant did nothing), both pass.

#### polluter

##### code

```java
// PathType.java
public final Splitter splitter() {
	return splitter; // return null
}
```

```java
// PollingWatchServiceTest.java
@Before
public void setUp() {
    fs = (JimfsFileSystem) Jimfs.newFileSystem(Configuration.unix());
    watcher =
        new PollingWatchService(
            fs.getDefaultView(),
            fs.getPathService(),
            new FileSystemState(new FakeFileTimeSource(), Runnables.doNothing()),
            4,
            MILLISECONDS);
}

@After
public void tearDown() throws IOException {
    watcher.close();
    fs.close();
    watcher = null;
    fs = null;
}

@Test(timeout = 2000)
public void testWatchForMultipleEventTypes() throws IOException, InterruptedException {
    JimfsPath path = createDirectory();
    watcher.register(path, ImmutableList.of(ENTRY_CREATE, ENTRY_DELETE, ENTRY_MODIFY));

    Files.createDirectory(path.resolve("foo"));
    Files.createFile(path.resolve("bar"));

    assertWatcherHasEvents(
        new Event<>(ENTRY_CREATE, 1, fs.getPath("bar")),
        new Event<>(ENTRY_CREATE, 1, fs.getPath("foo")));

    Files.createFile(path.resolve("baz"));
    Files.delete(path.resolve("bar"));
    Files.createFile(path.resolve("foo/bar"));

    assertWatcherHasEvents(
        new Event<>(ENTRY_CREATE, 1, fs.getPath("baz")),
        new Event<>(ENTRY_DELETE, 1, fs.getPath("bar")),
        new Event<>(ENTRY_MODIFY, 1, fs.getPath("foo")));

    Files.delete(path.resolve("foo/bar"));
    ensureTimeToPoll();
    Files.delete(path.resolve("foo"));

    assertWatcherHasEvents(
        new Event<>(ENTRY_MODIFY, 1, fs.getPath("foo")),
        new Event<>(ENTRY_DELETE, 1, fs.getPath("foo")));

    Files.createDirectories(path.resolve("foo/bar"));

    assertWatcherHasEvents(
        ImmutableList.<WatchEvent<?>>of(new Event<>(ENTRY_CREATE, 1, fs.getPath("foo"))),
        ImmutableList.<WatchEvent<?>>of(
            new Event<>(ENTRY_CREATE, 1, fs.getPath("foo")),
            new Event<>(ENTRY_MODIFY, 1, fs.getPath("foo"))));

    Files.delete(path.resolve("foo/bar"));
    Files.delete(path.resolve("foo"));

    assertWatcherHasEvents(
        ImmutableList.<WatchEvent<?>>of(new Event<>(ENTRY_DELETE, 1, fs.getPath("foo"))),
        ImmutableList.<WatchEvent<?>>of(
            new Event<>(ENTRY_MODIFY, 1, fs.getPath("foo")),
            new Event<>(ENTRY_DELETE, 1, fs.getPath("foo"))));
}
```

##### results

```
mvn test -Dtest=PollingWatchServiceTest#testWatchForMultipleEventTypes

[INFO] -------------------------------------------------------
[INFO]  T E S T S
[INFO] -------------------------------------------------------
[INFO] Running com.google.common.jimfs.PollingWatchServiceTest
[ERROR] Tests run: 2, Failures: 0, Errors: 2, Skipped: 0, Time elapsed: 0.046 s <<< FAILURE! -- in com.google.common.jimfs.PollingWatchServiceTest
[ERROR] com.google.common.jimfs.PollingWatchServiceTest.testWatchForMultipleEventTypes -- Time elapsed: 0.013 s <<< ERROR!
java.lang.ExceptionInInitializerError
        at com.google.common.jimfs.Configuration.unix(Configuration.java:86)
        at com.google.common.jimfs.PollingWatchServiceTest.setUp(PollingWatchServiceTest.java:60)
        at java.base/jdk.internal.reflect.NativeMethodAccessorImpl.invoke0(Native Method)
        at java.base/jdk.internal.reflect.NativeMethodAccessorImpl.invoke(NativeMethodAccessorImpl.java:77)
        at java.base/jdk.internal.reflect.DelegatingMethodAccessorImpl.invoke(DelegatingMethodAccessorImpl.java:43)
        at java.base/java.lang.reflect.Method.invoke(Method.java:569)
        at org.junit.runners.model.FrameworkMethod$1.runReflectiveCall(FrameworkMethod.java:59)
        at org.junit.internal.runners.model.ReflectiveCallable.run(ReflectiveCallable.java:12)
        at org.junit.runners.model.FrameworkMethod.invokeExplosively(FrameworkMethod.java:56)
        at org.junit.internal.runners.statements.RunBefores.invokeMethod(RunBefores.java:33)
        at org.junit.internal.runners.statements.RunBefores.evaluate(RunBefores.java:24)
        at org.junit.internal.runners.statements.RunAfters.evaluate(RunAfters.java:27)
        at org.junit.runners.ParentRunner$3.evaluate(ParentRunner.java:306)
        at org.junit.runners.BlockJUnit4ClassRunner$1.evaluate(BlockJUnit4ClassRunner.java:100)
        at org.junit.runners.ParentRunner.runLeaf(ParentRunner.java:366)
        at org.junit.runners.BlockJUnit4ClassRunner.runChild(BlockJUnit4ClassRunner.java:103)
        at org.junit.runners.BlockJUnit4ClassRunner.runChild(BlockJUnit4ClassRunner.java:63)
        at org.junit.runners.ParentRunner$4.run(ParentRunner.java:331)
        at org.junit.runners.ParentRunner$1.schedule(ParentRunner.java:79)
        at org.junit.runners.ParentRunner.runChildren(ParentRunner.java:329)
        at org.junit.runners.ParentRunner.access$100(ParentRunner.java:66)
        at org.junit.runners.ParentRunner$2.evaluate(ParentRunner.java:293)
        at org.junit.runners.ParentRunner$3.evaluate(ParentRunner.java:306)
        at org.junit.runners.ParentRunner.run(ParentRunner.java:413)
        at org.apache.maven.surefire.junit4.JUnit4Provider.execute(JUnit4Provider.java:316)
        at org.apache.maven.surefire.junit4.JUnit4Provider.executeWithRerun(JUnit4Provider.java:240)
        at org.apache.maven.surefire.junit4.JUnit4Provider.executeTestSet(JUnit4Provider.java:214)
        at org.apache.maven.surefire.junit4.JUnit4Provider.invoke(JUnit4Provider.java:155)
        at org.apache.maven.surefire.booter.ForkedBooter.runSuitesInProcess(ForkedBooter.java:385)
        at org.apache.maven.surefire.booter.ForkedBooter.execute(ForkedBooter.java:162)
        at org.apache.maven.surefire.booter.ForkedBooter.run(ForkedBooter.java:507)
        at org.apache.maven.surefire.booter.ForkedBooter.main(ForkedBooter.java:495)
Caused by: java.lang.NullPointerException: Cannot invoke "com.google.common.base.Splitter.split(java.lang.CharSequence)" because the return value of "com.google.common.jimfs.UnixPathType.splitter()" is null
        at com.google.common.jimfs.UnixPathType.parsePath(UnixPathType.java:47)
        at com.google.common.jimfs.Configuration$Builder.setRoots(Configuration.java:673)
        at com.google.common.jimfs.Configuration$UnixHolder.<clinit>(Configuration.java:93)
        ... 32 more

[ERROR] com.google.common.jimfs.PollingWatchServiceTest.testWatchForMultipleEventTypes -- Time elapsed: 0.014 s <<< ERROR!
java.lang.NullPointerException: Cannot invoke "com.google.common.jimfs.PollingWatchService.close()" because "this.watcher" is null
        at com.google.common.jimfs.PollingWatchServiceTest.tearDown(PollingWatchServiceTest.java:72)
        at java.base/jdk.internal.reflect.NativeMethodAccessorImpl.invoke0(Native Method)
        at java.base/jdk.internal.reflect.NativeMethodAccessorImpl.invoke(NativeMethodAccessorImpl.java:77)
        at java.base/jdk.internal.reflect.DelegatingMethodAccessorImpl.invoke(DelegatingMethodAccessorImpl.java:43)
        at java.base/java.lang.reflect.Method.invoke(Method.java:569)
        at org.junit.runners.model.FrameworkMethod$1.runReflectiveCall(FrameworkMethod.java:59)
        at org.junit.internal.runners.model.ReflectiveCallable.run(ReflectiveCallable.java:12)
        at org.junit.runners.model.FrameworkMethod.invokeExplosively(FrameworkMethod.java:56)
        at org.junit.internal.runners.statements.RunAfters.invokeMethod(RunAfters.java:46)
        at org.junit.internal.runners.statements.RunAfters.evaluate(RunAfters.java:33)
        at org.junit.runners.ParentRunner$3.evaluate(ParentRunner.java:306)
        at org.junit.runners.BlockJUnit4ClassRunner$1.evaluate(BlockJUnit4ClassRunner.java:100)
        at org.junit.runners.ParentRunner.runLeaf(ParentRunner.java:366)
        at org.junit.runners.BlockJUnit4ClassRunner.runChild(BlockJUnit4ClassRunner.java:103)
        at org.junit.runners.BlockJUnit4ClassRunner.runChild(BlockJUnit4ClassRunner.java:63)
        at org.junit.runners.ParentRunner$4.run(ParentRunner.java:331)
        at org.junit.runners.ParentRunner$1.schedule(ParentRunner.java:79)
        at org.junit.runners.ParentRunner.runChildren(ParentRunner.java:329)
        at org.junit.runners.ParentRunner.access$100(ParentRunner.java:66)
        at org.junit.runners.ParentRunner$2.evaluate(ParentRunner.java:293)
        at org.junit.runners.ParentRunner$3.evaluate(ParentRunner.java:306)
        at org.junit.runners.ParentRunner.run(ParentRunner.java:413)
        at org.apache.maven.surefire.junit4.JUnit4Provider.execute(JUnit4Provider.java:316)
        at org.apache.maven.surefire.junit4.JUnit4Provider.executeWithRerun(JUnit4Provider.java:240)
        at org.apache.maven.surefire.junit4.JUnit4Provider.executeTestSet(JUnit4Provider.java:214)
        at org.apache.maven.surefire.junit4.JUnit4Provider.invoke(JUnit4Provider.java:155)
        at org.apache.maven.surefire.booter.ForkedBooter.runSuitesInProcess(ForkedBooter.java:385)
        at org.apache.maven.surefire.booter.ForkedBooter.execute(ForkedBooter.java:162)
        at org.apache.maven.surefire.booter.ForkedBooter.run(ForkedBooter.java:507)
        at org.apache.maven.surefire.booter.ForkedBooter.main(ForkedBooter.java:495)

[INFO] 
[INFO] Results:
[INFO] 
[ERROR] Errors: 
[ERROR] com.google.common.jimfs.PollingWatchServiceTest.testWatchForMultipleEventTypes
[ERROR]   Run 1: PollingWatchServiceTest.setUp:60 ? ExceptionInInitializer
[ERROR]   Run 2: PollingWatchServiceTest.tearDown:72 NullPointer Cannot invoke "com.google.common.jimfs.PollingWatchService.close()" because "this.watcher" is null
[INFO] 
[INFO] 
[ERROR] Tests run: 1, Failures: 0, Errors: 1, Skipped: 0
[INFO] 
[INFO] ------------------------------------------------------------------------
```

```
mvn test -Dtest=ConfigurationTest#testFileSystemForDefaultOsXConfiguration

[INFO] -------------------------------------------------------
[INFO]  T E S T S
[INFO] -------------------------------------------------------
[INFO] Running com.google.common.jimfs.ConfigurationTest
[ERROR] Tests run: 1, Failures: 0, Errors: 1, Skipped: 0, Time elapsed: 0.048 s <<< FAILURE! -- in com.google.common.jimfs.ConfigurationTest
[ERROR] com.google.common.jimfs.ConfigurationTest.testFileSystemForDefaultOsXConfiguration -- Time elapsed: 0.013 s <<< ERROR!
java.lang.ExceptionInInitializerError
        at com.google.common.jimfs.Configuration.unix(Configuration.java:86)
        at com.google.common.jimfs.Configuration$OsxHolder.<clinit>(Configuration.java:139)
        at com.google.common.jimfs.Configuration.osX(Configuration.java:134)
        at com.google.common.jimfs.ConfigurationTest.testFileSystemForDefaultOsXConfiguration(ConfigurationTest.java:113)
        at java.base/jdk.internal.reflect.NativeMethodAccessorImpl.invoke0(Native Method)
        at java.base/jdk.internal.reflect.NativeMethodAccessorImpl.invoke(NativeMethodAccessorImpl.java:77)
        at java.base/jdk.internal.reflect.DelegatingMethodAccessorImpl.invoke(DelegatingMethodAccessorImpl.java:43)
        at java.base/java.lang.reflect.Method.invoke(Method.java:569)
        at org.junit.runners.model.FrameworkMethod$1.runReflectiveCall(FrameworkMethod.java:59)
        at org.junit.internal.runners.model.ReflectiveCallable.run(ReflectiveCallable.java:12)
        at org.junit.runners.model.FrameworkMethod.invokeExplosively(FrameworkMethod.java:56)
        at org.junit.internal.runners.statements.InvokeMethod.evaluate(InvokeMethod.java:17)
        at org.junit.runners.ParentRunner$3.evaluate(ParentRunner.java:306)
        at org.junit.runners.BlockJUnit4ClassRunner$1.evaluate(BlockJUnit4ClassRunner.java:100)
        at org.junit.runners.ParentRunner.runLeaf(ParentRunner.java:366)
        at org.junit.runners.BlockJUnit4ClassRunner.runChild(BlockJUnit4ClassRunner.java:103)
        at org.junit.runners.BlockJUnit4ClassRunner.runChild(BlockJUnit4ClassRunner.java:63)
        at org.junit.runners.ParentRunner$4.run(ParentRunner.java:331)
        at org.junit.runners.ParentRunner$1.schedule(ParentRunner.java:79)
        at org.junit.runners.ParentRunner.runChildren(ParentRunner.java:329)
        at org.junit.runners.ParentRunner.access$100(ParentRunner.java:66)
        at org.junit.runners.ParentRunner$2.evaluate(ParentRunner.java:293)
        at org.junit.runners.ParentRunner$3.evaluate(ParentRunner.java:306)
        at org.junit.runners.ParentRunner.run(ParentRunner.java:413)
        at org.apache.maven.surefire.junit4.JUnit4Provider.execute(JUnit4Provider.java:316)
        at org.apache.maven.surefire.junit4.JUnit4Provider.executeWithRerun(JUnit4Provider.java:240)
        at org.apache.maven.surefire.junit4.JUnit4Provider.executeTestSet(JUnit4Provider.java:214)
        at org.apache.maven.surefire.junit4.JUnit4Provider.invoke(JUnit4Provider.java:155)
        at org.apache.maven.surefire.booter.ForkedBooter.runSuitesInProcess(ForkedBooter.java:385)
        at org.apache.maven.surefire.booter.ForkedBooter.execute(ForkedBooter.java:162)
        at org.apache.maven.surefire.booter.ForkedBooter.run(ForkedBooter.java:507)
        at org.apache.maven.surefire.booter.ForkedBooter.main(ForkedBooter.java:495)
Caused by: java.lang.NullPointerException: Cannot invoke "com.google.common.base.Splitter.split(java.lang.CharSequence)" because the return value of "com.google.common.jimfs.UnixPathType.splitter()" is null
        at com.google.common.jimfs.UnixPathType.parsePath(UnixPathType.java:47)
        at com.google.common.jimfs.Configuration$Builder.setRoots(Configuration.java:673)
        at com.google.common.jimfs.Configuration$UnixHolder.<clinit>(Configuration.java:93)
        ... 32 more

[INFO] 
[INFO] Results:
[INFO] 
[ERROR] Errors: 
[ERROR]   ConfigurationTest.testFileSystemForDefaultOsXConfiguration:113 ? ExceptionInInitializer
[INFO] 
[ERROR] Tests run: 1, Failures: 0, Errors: 1, Skipped: 0
[INFO] 
[INFO] ------------------------------------------------------------------------
```

#### victim

##### code

```java
// SystemJimfsFileSystemProvider.java
@Override
public String getScheme() {
	return URI_SCHEME; // return new String()
}
```

##### results

```
mvn test -Dtest=PollingWatchServiceTest#testWatchForMultipleEventTypes

[INFO] -------------------------------------------------------
[INFO]  T E S T S
[INFO] -------------------------------------------------------
[INFO] Running com.google.common.jimfs.PollingWatchServiceTest
[INFO] Tests run: 1, Failures: 0, Errors: 0, Skipped: 0, Time elapsed: 0.394 s -- in com.google.common.jimfs.PollingWatchServiceTest
[INFO] 
[INFO] Results:
[INFO] 
[INFO] Tests run: 1, Failures: 0, Errors: 0, Skipped: 0
[INFO] 
[INFO] ------------------------------------------------------------------------
```

```
mvn test -Dtest=ConfigurationTest#testFileSystemForDefaultOsXConfiguration

[INFO] -------------------------------------------------------
[INFO]  T E S T S
[INFO] -------------------------------------------------------
[INFO] Running com.google.common.jimfs.ConfigurationTest
[INFO] Tests run: 1, Failures: 0, Errors: 0, Skipped: 0, Time elapsed: 0.097 s -- in com.google.common.jimfs.ConfigurationTest
[INFO] 
[INFO] Results:
[INFO] 
[INFO] Tests run: 1, Failures: 0, Errors: 0, Skipped: 0
[INFO] 
[INFO] ------------------------------------------------------------------------
```

### 3470 (3) -- Survived

Run 3-jimfs_5-0-edge_9-0-mid.json, both fail.

Run 3-jimfs_5-0-edge_9-0-mid_dummy.json (polluted mutant did nothing), both pass.

#### polluter

The same as 3317.

#### victim

##### code

```Java
// SystemJimfsFileSystemProvider.java
private static boolean isValidFileSystemUri(URI uri) {
    return isNullOrEmpty(uri.getPath())
        && isNullOrEmpty(uri.getQuery())
        && isNullOrEmpty(uri.getFragment()); // return true
}
```

##### results

```
mvn test -Dtest=PollingWatchServiceTest#testWatchForMultipleEventTypes

[INFO] -------------------------------------------------------
[INFO]  T E S T S
[INFO] -------------------------------------------------------
[INFO] Running com.google.common.jimfs.PollingWatchServiceTest
[INFO] Tests run: 1, Failures: 0, Errors: 0, Skipped: 0, Time elapsed: 0.375 s -- in com.google.common.jimfs.PollingWatchServiceTest
[INFO] 
[INFO] Results:
[INFO] 
[INFO] Tests run: 1, Failures: 0, Errors: 0, Skipped: 0
[INFO] 
[INFO] ------------------------------------------------------------------------
```

```
mvn test -Dtest=ConfigurationTest#testFileSystemForDefaultOsXConfiguration

[INFO] -------------------------------------------------------
[INFO]  T E S T S
[INFO] -------------------------------------------------------
[INFO] Running com.google.common.jimfs.ConfigurationTest
[INFO] Tests run: 1, Failures: 0, Errors: 0, Skipped: 0, Time elapsed: 0.109 s -- in com.google.common.jimfs.ConfigurationTest
[INFO] 
[INFO] Results:
[INFO] 
[INFO] Tests run: 1, Failures: 0, Errors: 0, Skipped: 0
[INFO] 
[INFO] ------------------------------------------------------------------------
```

### 3714 (4) -- Survived

Run 4-jimfs_5-0-mid_9-0-mid.json, both fail.

Run 4-jimfs_5-0-mid_9-0-mid_dummy.json (polluted mutant did nothing), both pass.

#### polluter

The same as 3317.

#### victim

##### code

```java
// SystemJimfsFileSystemProvider.java
@Override
public FileSystem newFileSystem(URI uri, Map<String, ?> env) throws IOException {
    checkArgument(
        uri.getScheme().equalsIgnoreCase(URI_SCHEME),
        "uri (%s) scheme must be '%s'",
        uri,
        URI_SCHEME); // remove call
    checkArgument(
        isValidFileSystemUri(uri), "uri (%s) may not have a path, query or fragment", uri);
    checkArgument(
        env.get(FILE_SYSTEM_KEY) instanceof FileSystem,
        "env map (%s) must contain key '%s' mapped to an instance of %s",
        env,
        FILE_SYSTEM_KEY,
        FileSystem.class);

    FileSystem fileSystem = (FileSystem) env.get(FILE_SYSTEM_KEY);
    if (fileSystems.putIfAbsent(uri, fileSystem) != null) {
      throw new FileSystemAlreadyExistsException(uri.toString());
    }
    return fileSystem;
}
```

##### results

```
mvn test -Dtest=PollingWatchServiceTest#testWatchForMultipleEventTypes

[INFO] -------------------------------------------------------
[INFO]  T E S T S
[INFO] -------------------------------------------------------
[INFO] Running com.google.common.jimfs.PollingWatchServiceTest
[INFO] Tests run: 1, Failures: 0, Errors: 0, Skipped: 0, Time elapsed: 0.366 s -- in com.google.common.jimfs.PollingWatchServiceTest
[INFO] 
[INFO] Results:
[INFO] 
[INFO] Tests run: 1, Failures: 0, Errors: 0, Skipped: 0
[INFO] 
[INFO] ------------------------------------------------------------------------
```

```
mvn test -Dtest=ConfigurationTest#testFileSystemForDefaultOsXConfiguration

[INFO] -------------------------------------------------------
[INFO]  T E S T S
[INFO] -------------------------------------------------------
[INFO] Running com.google.common.jimfs.ConfigurationTest
[INFO] Tests run: 1, Failures: 0, Errors: 0, Skipped: 0, Time elapsed: 0.103 s -- in com.google.common.jimfs.ConfigurationTest
[INFO] 
[INFO] Results:
[INFO] 
[INFO] Tests run: 1, Failures: 0, Errors: 0, Skipped: 0
[INFO] 
[INFO] ------------------------------------------------------------------------
```

### 4394 (8) -- Survived

Run 8-jimfs_6-0-edge_8-0-mid.json, both fail.

Run 8-jimfs_6-0-edge_8-0-mid_dummy.json (polluted mutant did nothing), both pass.

#### polluter

The same as 3317.

#### victim

##### code

```java
// FileSystemState.java
public FileTime now() {
    return fileTimeSource.now(); // return null
}
```

##### results

```
mvn test -Dtest=PollingWatchServiceTest#testWatchForMultipleEventTypes

[INFO] -------------------------------------------------------
[INFO]  T E S T S
[INFO] -------------------------------------------------------
[INFO] Running com.google.common.jimfs.PollingWatchServiceTest
[ERROR] Tests run: 1, Failures: 0, Errors: 1, Skipped: 0, Time elapsed: 2.104 s <<< FAILURE! -- in com.google.common.jimfs.PollingWatchServiceTest
[ERROR] com.google.common.jimfs.PollingWatchServiceTest.testWatchForMultipleEventTypes -- Time elapsed: 2.070 s <<< ERROR!
org.junit.runners.model.TestTimedOutException: test timed out after 2000 milliseconds
        at java.base@17.0.12/jdk.internal.misc.Unsafe.park(Native Method)
        at java.base@17.0.12/java.util.concurrent.locks.LockSupport.park(LockSupport.java:341)
        at java.base@17.0.12/java.util.concurrent.locks.AbstractQueuedSynchronizer$ConditionNode.block(AbstractQueuedSynchronizer.java:506)
        at java.base@17.0.12/java.util.concurrent.ForkJoinPool.unmanagedBlock(ForkJoinPool.java:3465)
        at java.base@17.0.12/java.util.concurrent.ForkJoinPool.managedBlock(ForkJoinPool.java:3436)
        at java.base@17.0.12/java.util.concurrent.locks.AbstractQueuedSynchronizer$ConditionObject.await(AbstractQueuedSynchronizer.java:1625)
        at java.base@17.0.12/java.util.concurrent.LinkedBlockingQueue.take(LinkedBlockingQueue.java:435)
        at app//com.google.common.jimfs.AbstractWatchService.take(AbstractWatchService.java:109)
        at app//com.google.common.jimfs.PollingWatchServiceTest.assertWatcherHasEvents(PollingWatchServiceTest.java:227)
        at app//com.google.common.jimfs.PollingWatchServiceTest.assertWatcherHasEvents(PollingWatchServiceTest.java:221)
        at app//com.google.common.jimfs.PollingWatchServiceTest.testWatchForMultipleEventTypes(PollingWatchServiceTest.java:183)
        at java.base@17.0.12/jdk.internal.reflect.NativeMethodAccessorImpl.invoke0(Native Method)
        at java.base@17.0.12/jdk.internal.reflect.NativeMethodAccessorImpl.invoke(NativeMethodAccessorImpl.java:77)
        at java.base@17.0.12/jdk.internal.reflect.DelegatingMethodAccessorImpl.invoke(DelegatingMethodAccessorImpl.java:43)
        at java.base@17.0.12/java.lang.reflect.Method.invoke(Method.java:569)
        at app//org.junit.runners.model.FrameworkMethod$1.runReflectiveCall(FrameworkMethod.java:59)
        at app//org.junit.internal.runners.model.ReflectiveCallable.run(ReflectiveCallable.java:12)
        at app//org.junit.runners.model.FrameworkMethod.invokeExplosively(FrameworkMethod.java:56)
        at app//org.junit.internal.runners.statements.InvokeMethod.evaluate(InvokeMethod.java:17)
        at app//org.junit.internal.runners.statements.FailOnTimeout$CallableStatement.call(FailOnTimeout.java:299)
        at app//org.junit.internal.runners.statements.FailOnTimeout$CallableStatement.call(FailOnTimeout.java:293)
        at java.base@17.0.12/java.util.concurrent.FutureTask.run(FutureTask.java:264)
        at java.base@17.0.12/java.lang.Thread.run(Thread.java:840)

[INFO] 
[INFO] Results:
[INFO] 
[ERROR] Errors: 
[ERROR]   PollingWatchServiceTest.testWatchForMultipleEventTypes:183->assertWatcherHasEvents:221->assertWatcherHasEvents:227 ? TestTimedOut test timed out after 2000 milliseconds
[INFO] 
[ERROR] Tests run: 1, Failures: 0, Errors: 1, Skipped: 0
[INFO] 
[INFO] ------------------------------------------------------------------------
```

```
mvn test -Dtest=ConfigurationTest#testFileSystemForDefaultOsXConfiguration

[INFO] -------------------------------------------------------
[INFO]  T E S T S
[INFO] -------------------------------------------------------
[INFO] Running com.google.common.jimfs.ConfigurationTest
[INFO] Tests run: 1, Failures: 0, Errors: 0, Skipped: 0, Time elapsed: 0.095 s -- in com.google.common.jimfs.ConfigurationTest
[INFO] 
[INFO] Results:
[INFO] 
[INFO] Tests run: 1, Failures: 0, Errors: 0, Skipped: 0
[INFO] 
[INFO] ------------------------------------------------------------------------
```

### 4493 (9) -- Survived

Run 9-jimfs_6-0-edge_9-0-mid.json, both fail.

Run 9-jimfs_6-0-edge_9-0-mid_dummy.json (polluted mutant did nothing), both pass.

#### polluter

The same as 3317.

#### victim

##### code

```java
// victim
// FileSystemState.java
@CanIgnoreReturnValue
public <C extends Closeable> C register(C resource) {
    checkOpen(); // remove call
    registering.incrementAndGet();
    try {
      checkOpen();
      resources.add(resource);
      return resource;
    } finally {
      registering.decrementAndGet();
    }
}
```

##### results

```
mvn test -Dtest=PollingWatchServiceTest#testWatchForMultipleEventTypes

[INFO] -------------------------------------------------------
[INFO]  T E S T S
[INFO] -------------------------------------------------------
[INFO] Running com.google.common.jimfs.PollingWatchServiceTest
[INFO] Tests run: 1, Failures: 0, Errors: 0, Skipped: 0, Time elapsed: 0.370 s -- in com.google.common.jimfs.PollingWatchServiceTest
[INFO] 
[INFO] Results:
[INFO] 
[INFO] Tests run: 1, Failures: 0, Errors: 0, Skipped: 0
[INFO] 
[INFO] ------------------------------------------------------------------------
```

```
mvn test -Dtest=ConfigurationTest#testFileSystemForDefaultOsXConfiguration

[INFO] -------------------------------------------------------
[INFO]  T E S T S
[INFO] -------------------------------------------------------
[INFO] Running com.google.common.jimfs.ConfigurationTest
[INFO] Tests run: 1, Failures: 0, Errors: 0, Skipped: 0, Time elapsed: 0.106 s -- in com.google.common.jimfs.ConfigurationTest
[INFO] 
[INFO] Results:
[INFO] 
[INFO] Tests run: 1, Failures: 0, Errors: 0, Skipped: 0
[INFO] 
[INFO] ------------------------------------------------------------------------
```

### 4586 (10) -- Survived

Run 10-jimfs_6-0-edge_9-0-edge.json, both fail.

Run 10-jimfs_6-0-edge_9-0-edge_dummy.json (polluted mutant did nothing), both pass.

#### polluter

The same as 3317.

#### victim

##### code

```java
// FileSystemState.java
@CanIgnoreReturnValue
public <C extends Closeable> C register(C resource) {
    checkOpen();
    registering.incrementAndGet();
    try {
      checkOpen(); // remove call
      resources.add(resource);
      return resource;
    } finally {
      registering.decrementAndGet();
    }
}
```

##### results

```
mvn test -Dtest=PollingWatchServiceTest#testWatchForMultipleEventTypes

[INFO] -------------------------------------------------------
[INFO]  T E S T S
[INFO] -------------------------------------------------------
[INFO] Running com.google.common.jimfs.PollingWatchServiceTest
[INFO] Tests run: 1, Failures: 0, Errors: 0, Skipped: 0, Time elapsed: 0.370 s -- in com.google.common.jimfs.PollingWatchServiceTest
[INFO] 
[INFO] Results:
[INFO] 
[INFO] Tests run: 1, Failures: 0, Errors: 0, Skipped: 0
[INFO] 
[INFO] ------------------------------------------------------------------------
```

```
mvn test -Dtest=ConfigurationTest#testFileSystemForDefaultOsXConfiguration

[INFO] -------------------------------------------------------
[INFO]  T E S T S
[INFO] -------------------------------------------------------
[INFO] Running com.google.common.jimfs.ConfigurationTest
[INFO] Tests run: 1, Failures: 0, Errors: 0, Skipped: 0, Time elapsed: 0.106 s -- in com.google.common.jimfs.ConfigurationTest
[INFO] 
[INFO] Results:
[INFO] 
[INFO] Tests run: 1, Failures: 0, Errors: 0, Skipped: 0
[INFO] 
[INFO] ------------------------------------------------------------------------
```

### 4679 (11) -- Survived

Run 11-jimfs_6-0-edge_9-0-edge.json, both fail.

Run 11-jimfs_6-0-edge_9-0-edge_dummy.json (polluted mutant did nothing), both pass.

#### polluter

The same as 3317.

#### victim

##### code

```java
// FileSystemState.java
@CanIgnoreReturnValue
public <C extends Closeable> C register(C resource) {
    checkOpen();
    registering.incrementAndGet();
    try {
      checkOpen();
      resources.add(resource);
      return resource; //return null
    } finally {
      registering.decrementAndGet();
    }
}
```

##### results

```
mvn test -Dtest=PollingWatchServiceTest#testWatchForMultipleEventTypes

[INFO] -------------------------------------------------------
[INFO]  T E S T S
[INFO] -------------------------------------------------------
[INFO] Running com.google.common.jimfs.PollingWatchServiceTest
[INFO] Tests run: 1, Failures: 0, Errors: 0, Skipped: 0, Time elapsed: 0.370 s -- in com.google.common.jimfs.PollingWatchServiceTest
[INFO] 
[INFO] Results:
[INFO] 
[INFO] Tests run: 1, Failures: 0, Errors: 0, Skipped: 0
[INFO] 
[INFO] ------------------------------------------------------------------------
```

```
mvn test -Dtest=ConfigurationTest#testFileSystemForDefaultOsXConfiguration

[INFO] -------------------------------------------------------
[INFO]  T E S T S
[INFO] -------------------------------------------------------
[INFO] Running com.google.common.jimfs.ConfigurationTest
[INFO] Tests run: 1, Failures: 0, Errors: 0, Skipped: 0, Time elapsed: 0.106 s -- in com.google.common.jimfs.ConfigurationTest
[INFO] 
[INFO] Results:
[INFO] 
[INFO] Tests run: 1, Failures: 0, Errors: 0, Skipped: 0
[INFO] 
[INFO] ------------------------------------------------------------------------
```

### 3870 (5) -- Survived

Run 5-jimfs_5-0-mid_7-0-edge.json, both fail.

Run 5-jimfs_5-0-mid_7-0-edge_dummy.json (polluted mutant did nothing), both pass.

#### polluter

##### code

```java
// PathType.java
public static PathType unix() {
    return UnixPathType.INSTANCE; // return null
}
```

```java
// JimfsPathTest.java
private final PathService pathService = PathServiceTest.fakeUnixPathService();

@Test
public void testAbsoluteMultiNamePath_fourNames() {
    new PathTester(pathService, "/foo/bar/baz/test")
        .root("/")
        .names("foo", "bar", "baz", "test")
        .test("/foo/bar/baz/test");
}
```

##### results

```
mvn test -Dtest=JimfsPathTest#testAbsoluteMultiNamePath_fourNames

[INFO] -------------------------------------------------------
[INFO]  T E S T S
[INFO] -------------------------------------------------------
[INFO] Running com.google.common.jimfs.JimfsPathTest
[ERROR] Tests run: 1, Failures: 0, Errors: 1, Skipped: 0, Time elapsed: 0.048 s <<< FAILURE! -- in com.google.common.jimfs.JimfsPathTest
[ERROR] com.google.common.jimfs.JimfsPathTest.testAbsoluteMultiNamePath_fourNames -- Time elapsed: 0.011 s <<< ERROR!
java.lang.ExceptionInInitializerError
        at com.google.common.jimfs.Configuration.unix(Configuration.java:86)
        at com.google.common.jimfs.PathServiceTest.<clinit>(PathServiceTest.java:259)
        at com.google.common.jimfs.JimfsPathTest.<init>(JimfsPathTest.java:40)
        at java.base/jdk.internal.reflect.NativeConstructorAccessorImpl.newInstance0(Native Method)
        at java.base/jdk.internal.reflect.NativeConstructorAccessorImpl.newInstance(NativeConstructorAccessorImpl.java:77)
        at java.base/jdk.internal.reflect.DelegatingConstructorAccessorImpl.newInstance(DelegatingConstructorAccessorImpl.java:45)
        at java.base/java.lang.reflect.Constructor.newInstanceWithCaller(Constructor.java:500)
        at java.base/java.lang.reflect.Constructor.newInstance(Constructor.java:481)
        at org.junit.runners.BlockJUnit4ClassRunner.createTest(BlockJUnit4ClassRunner.java:250)
        at org.junit.runners.BlockJUnit4ClassRunner.createTest(BlockJUnit4ClassRunner.java:260)
        at org.junit.runners.BlockJUnit4ClassRunner$2.runReflectiveCall(BlockJUnit4ClassRunner.java:309)
        at org.junit.internal.runners.model.ReflectiveCallable.run(ReflectiveCallable.java:12)
        at org.junit.runners.BlockJUnit4ClassRunner.methodBlock(BlockJUnit4ClassRunner.java:306)
        at org.junit.runners.BlockJUnit4ClassRunner$1.evaluate(BlockJUnit4ClassRunner.java:100)
        at org.junit.runners.ParentRunner.runLeaf(ParentRunner.java:366)
        at org.junit.runners.BlockJUnit4ClassRunner.runChild(BlockJUnit4ClassRunner.java:103)
        at org.junit.runners.BlockJUnit4ClassRunner.runChild(BlockJUnit4ClassRunner.java:63)
        at org.junit.runners.ParentRunner$4.run(ParentRunner.java:331)
        at org.junit.runners.ParentRunner$1.schedule(ParentRunner.java:79)
        at org.junit.runners.ParentRunner.runChildren(ParentRunner.java:329)
        at org.junit.runners.ParentRunner.access$100(ParentRunner.java:66)
        at org.junit.runners.ParentRunner$2.evaluate(ParentRunner.java:293)
        at org.junit.runners.ParentRunner$3.evaluate(ParentRunner.java:306)
        at org.junit.runners.ParentRunner.run(ParentRunner.java:413)
        at org.apache.maven.surefire.junit4.JUnit4Provider.execute(JUnit4Provider.java:316)
        at org.apache.maven.surefire.junit4.JUnit4Provider.executeWithRerun(JUnit4Provider.java:240)
        at org.apache.maven.surefire.junit4.JUnit4Provider.executeTestSet(JUnit4Provider.java:214)
        at org.apache.maven.surefire.junit4.JUnit4Provider.invoke(JUnit4Provider.java:155)
        at org.apache.maven.surefire.booter.ForkedBooter.runSuitesInProcess(ForkedBooter.java:385)
        at org.apache.maven.surefire.booter.ForkedBooter.execute(ForkedBooter.java:162)
        at org.apache.maven.surefire.booter.ForkedBooter.run(ForkedBooter.java:507)
        at org.apache.maven.surefire.booter.ForkedBooter.main(ForkedBooter.java:495)
Caused by: java.lang.NullPointerException
        at com.google.common.base.Preconditions.checkNotNull(Preconditions.java:906)
        at com.google.common.jimfs.Configuration$Builder.<init>(Configuration.java:360)
        at com.google.common.jimfs.Configuration$Builder.<init>(Configuration.java:322)
        at com.google.common.jimfs.Configuration.builder(Configuration.java:219)
        at com.google.common.jimfs.Configuration$UnixHolder.<clinit>(Configuration.java:91)
        ... 32 more

[INFO] 
[INFO] Results:
[INFO] 
[ERROR] Errors: 
[ERROR]   JimfsPathTest.<init>:40 ? ExceptionInInitializer
[INFO] 
[ERROR] Tests run: 1, Failures: 0, Errors: 1, Skipped: 0
[INFO] 
[INFO] ------------------------------------------------------------------------
```

```
mvn test -Dtest=ConfigurationTest#testFileSystemForDefaultOsXConfiguration

[INFO] -------------------------------------------------------
[INFO]  T E S T S
[INFO] -------------------------------------------------------
[INFO] Running com.google.common.jimfs.ConfigurationTest
[ERROR] Tests run: 1, Failures: 0, Errors: 1, Skipped: 0, Time elapsed: 0.042 s <<< FAILURE! -- in com.google.common.jimfs.ConfigurationTest
[ERROR] com.google.common.jimfs.ConfigurationTest.testFileSystemForDefaultOsXConfiguration -- Time elapsed: 0.009 s <<< ERROR!
java.lang.ExceptionInInitializerError
        at com.google.common.jimfs.Configuration.unix(Configuration.java:86)
        at com.google.common.jimfs.Configuration$OsxHolder.<clinit>(Configuration.java:139)
        at com.google.common.jimfs.Configuration.osX(Configuration.java:134)
        at com.google.common.jimfs.ConfigurationTest.testFileSystemForDefaultOsXConfiguration(ConfigurationTest.java:113)
        at java.base/jdk.internal.reflect.NativeMethodAccessorImpl.invoke0(Native Method)
        at java.base/jdk.internal.reflect.NativeMethodAccessorImpl.invoke(NativeMethodAccessorImpl.java:77)
        at java.base/jdk.internal.reflect.DelegatingMethodAccessorImpl.invoke(DelegatingMethodAccessorImpl.java:43)
        at java.base/java.lang.reflect.Method.invoke(Method.java:569)
        at org.junit.runners.model.FrameworkMethod$1.runReflectiveCall(FrameworkMethod.java:59)
        at org.junit.internal.runners.model.ReflectiveCallable.run(ReflectiveCallable.java:12)
        at org.junit.runners.model.FrameworkMethod.invokeExplosively(FrameworkMethod.java:56)
        at org.junit.internal.runners.statements.InvokeMethod.evaluate(InvokeMethod.java:17)
        at org.junit.runners.ParentRunner$3.evaluate(ParentRunner.java:306)
        at org.junit.runners.BlockJUnit4ClassRunner$1.evaluate(BlockJUnit4ClassRunner.java:100)
        at org.junit.runners.ParentRunner.runLeaf(ParentRunner.java:366)
        at org.junit.runners.BlockJUnit4ClassRunner.runChild(BlockJUnit4ClassRunner.java:103)
        at org.junit.runners.BlockJUnit4ClassRunner.runChild(BlockJUnit4ClassRunner.java:63)
        at org.junit.runners.ParentRunner$4.run(ParentRunner.java:331)
        at org.junit.runners.ParentRunner$1.schedule(ParentRunner.java:79)
        at org.junit.runners.ParentRunner.runChildren(ParentRunner.java:329)
        at org.junit.runners.ParentRunner.access$100(ParentRunner.java:66)
        at org.junit.runners.ParentRunner$2.evaluate(ParentRunner.java:293)
        at org.junit.runners.ParentRunner$3.evaluate(ParentRunner.java:306)
        at org.junit.runners.ParentRunner.run(ParentRunner.java:413)
        at org.apache.maven.surefire.junit4.JUnit4Provider.execute(JUnit4Provider.java:316)
        at org.apache.maven.surefire.junit4.JUnit4Provider.executeWithRerun(JUnit4Provider.java:240)
        at org.apache.maven.surefire.junit4.JUnit4Provider.executeTestSet(JUnit4Provider.java:214)
        at org.apache.maven.surefire.junit4.JUnit4Provider.invoke(JUnit4Provider.java:155)
        at org.apache.maven.surefire.booter.ForkedBooter.runSuitesInProcess(ForkedBooter.java:385)
        at org.apache.maven.surefire.booter.ForkedBooter.execute(ForkedBooter.java:162)
        at org.apache.maven.surefire.booter.ForkedBooter.run(ForkedBooter.java:507)
        at org.apache.maven.surefire.booter.ForkedBooter.main(ForkedBooter.java:495)
Caused by: java.lang.NullPointerException
        at com.google.common.base.Preconditions.checkNotNull(Preconditions.java:906)
        at com.google.common.jimfs.Configuration$Builder.<init>(Configuration.java:360)
        at com.google.common.jimfs.Configuration$Builder.<init>(Configuration.java:322)
        at com.google.common.jimfs.Configuration.builder(Configuration.java:219)
        at com.google.common.jimfs.Configuration$UnixHolder.<clinit>(Configuration.java:91)
        ... 32 more

[INFO] 
[INFO] Results:
[INFO] 
[ERROR] Errors: 
[ERROR]   ConfigurationTest.testFileSystemForDefaultOsXConfiguration:113 ? ExceptionInInitializer
[INFO] 
[ERROR] Tests run: 1, Failures: 0, Errors: 1, Skipped: 0
[INFO] 
[INFO] ------------------------------------------------------------------------
```

#### victim

##### code

```java
// SystemJimfsFileSystemProvider.java
@Override
public FileSystem newFileSystem(URI uri, Map<String, ?> env) throws IOException {
    checkArgument(
        uri.getScheme().equalsIgnoreCase(URI_SCHEME),
        "uri (%s) scheme must be '%s'",
        uri,
        URI_SCHEME);
    checkArgument(
        isValidFileSystemUri(uri), "uri (%s) may not have a path, query or fragment", uri); // remove call
    checkArgument(
        env.get(FILE_SYSTEM_KEY) instanceof FileSystem,
        "env map (%s) must contain key '%s' mapped to an instance of %s",
        env,
        FILE_SYSTEM_KEY,
        FileSystem.class);

    FileSystem fileSystem = (FileSystem) env.get(FILE_SYSTEM_KEY);
    if (fileSystems.putIfAbsent(uri, fileSystem) != null) {
      throw new FileSystemAlreadyExistsException(uri.toString());
    }
    return fileSystem;
}
```

##### results

```
mvn test -Dtest=JimfsPathTest#testAbsoluteMultiNamePath_fourNames

[INFO] -------------------------------------------------------
[INFO]  T E S T S
[INFO] -------------------------------------------------------
[INFO] Running com.google.common.jimfs.JimfsPathTest
[INFO] Tests run: 1, Failures: 0, Errors: 0, Skipped: 0, Time elapsed: 0.089 s -- in com.google.common.jimfs.JimfsPathTest
[INFO] 
[INFO] Results:
[INFO] 
[INFO] Tests run: 1, Failures: 0, Errors: 0, Skipped: 0
[INFO] 
[INFO] ------------------------------------------------------------------------
```

```
mvn test -Dtest=ConfigurationTest#testFileSystemForDefaultOsXConfiguration

[INFO] -------------------------------------------------------
[INFO]  T E S T S
[INFO] -------------------------------------------------------
[INFO] Running com.google.common.jimfs.ConfigurationTest
[INFO] Tests run: 1, Failures: 0, Errors: 0, Skipped: 0, Time elapsed: 0.110 s -- in com.google.common.jimfs.ConfigurationTest
[INFO] 
[INFO] Results:
[INFO] 
[INFO] Tests run: 1, Failures: 0, Errors: 0, Skipped: 0
[INFO] 
[INFO] ------------------------------------------------------------------------
```

### 4026 (6) -- Survived

Run 6-jimfs_5-0-mid_7-0-edge.json, both fail.

Run 6-jimfs_5-0-mid_7-0-edge_dummy.json (polluted mutant did nothing), both pass.

#### polluter

The same as 3870.

#### victim

##### code

```java
// SystemJimfsFileSystemProvider.java
@Override
public FileSystem newFileSystem(URI uri, Map<String, ?> env) throws IOException {
    checkArgument(
        uri.getScheme().equalsIgnoreCase(URI_SCHEME),
        "uri (%s) scheme must be '%s'",
        uri,
        URI_SCHEME);
    checkArgument(
        isValidFileSystemUri(uri), "uri (%s) may not have a path, query or fragment", uri);
    checkArgument(
        env.get(FILE_SYSTEM_KEY) instanceof FileSystem,
        "env map (%s) must contain key '%s' mapped to an instance of %s",
        env,
        FILE_SYSTEM_KEY,
        FileSystem.class); // remove call

    FileSystem fileSystem = (FileSystem) env.get(FILE_SYSTEM_KEY);
    if (fileSystems.putIfAbsent(uri, fileSystem) != null) {
      throw new FileSystemAlreadyExistsException(uri.toString());
    }
    return fileSystem;
}
```

##### results

```
mvn test -Dtest=JimfsPathTest#testAbsoluteMultiNamePath_fourNames

[INFO] -------------------------------------------------------
[INFO]  T E S T S
[INFO] -------------------------------------------------------
[INFO] Running com.google.common.jimfs.JimfsPathTest
[INFO] Tests run: 1, Failures: 0, Errors: 0, Skipped: 0, Time elapsed: 0.090 s -- in com.google.common.jimfs.JimfsPathTest
[INFO] 
[INFO] Results:
[INFO] 
[INFO] Tests run: 1, Failures: 0, Errors: 0, Skipped: 0
[INFO] 
[INFO] ------------------------------------------------------------------------
```

```
mvn test -Dtest=ConfigurationTest#testFileSystemForDefaultOsXConfiguration

[INFO] -------------------------------------------------------
[INFO]  T E S T S
[INFO] -------------------------------------------------------
[INFO] Running com.google.common.jimfs.ConfigurationTest
[INFO] Tests run: 1, Failures: 0, Errors: 0, Skipped: 0, Time elapsed: 0.099 s -- in com.google.common.jimfs.ConfigurationTest
[INFO] 
[INFO] Results:
[INFO] 
[INFO] Tests run: 1, Failures: 0, Errors: 0, Skipped: 0
[INFO] 
[INFO] ------------------------------------------------------------------------
```

### 4182 (7) -- Survived

Run 7-jimfs_5-0-mid_7-0-edge.json, both fail.

Run 7-jimfs_5-0-mid_7-0-edge_dummy.json (polluted mutant did nothing), both pass.

#### polluter

The same as 3870.

#### victim

##### code

```java
// SystemJimfsFileSystemProvider.java
@Override
public FileSystem newFileSystem(URI uri, Map<String, ?> env) throws IOException {
    checkArgument(
        uri.getScheme().equalsIgnoreCase(URI_SCHEME),
        "uri (%s) scheme must be '%s'",
        uri,
        URI_SCHEME);
    checkArgument(
        isValidFileSystemUri(uri), "uri (%s) may not have a path, query or fragment", uri);
    checkArgument(
        env.get(FILE_SYSTEM_KEY) instanceof FileSystem,
        "env map (%s) must contain key '%s' mapped to an instance of %s",
        env,
        FILE_SYSTEM_KEY,
        FileSystem.class);

    FileSystem fileSystem = (FileSystem) env.get(FILE_SYSTEM_KEY);
    if (fileSystems.putIfAbsent(uri, fileSystem) != null) {
      throw new FileSystemAlreadyExistsException(uri.toString());
    }
    return fileSystem; // return null
}
```

##### results

```
mvn test -Dtest=JimfsPathTest#testAbsoluteMultiNamePath_fourNames

[INFO] -------------------------------------------------------
[INFO]  T E S T S
[INFO] -------------------------------------------------------
[INFO] Running com.google.common.jimfs.JimfsPathTest
[INFO] Tests run: 1, Failures: 0, Errors: 0, Skipped: 0, Time elapsed: 0.087 s -- in com.google.common.jimfs.JimfsPathTest
[INFO] 
[INFO] Results:
[INFO] 
[INFO] Tests run: 1, Failures: 0, Errors: 0, Skipped: 0
[INFO] 
[INFO] ------------------------------------------------------------------------
```

```
mvn test -Dtest=ConfigurationTest#testFileSystemForDefaultOsXConfiguration

[INFO] -------------------------------------------------------
[INFO]  T E S T S
[INFO] -------------------------------------------------------
[INFO] Running com.google.common.jimfs.ConfigurationTest
[INFO] Tests run: 1, Failures: 0, Errors: 0, Skipped: 0, Time elapsed: 0.100 s -- in com.google.common.jimfs.ConfigurationTest
[INFO] 
[INFO] Results:
[INFO] 
[INFO] Tests run: 1, Failures: 0, Errors: 0, Skipped: 0
[INFO] 
[INFO] ------------------------------------------------------------------------
```

### 4996 (12) -- Unknown

The mutant that this pair comes from is not always found. It depends on other mutants.

Run 12-jimfs_2-0-mid_9-0-edge.json, both fail.

Run 12-jimfs_2-0-mid_9-0-edge_dummy.json (polluted mutant did nothing), only victim exists and passes.

#### polluter

##### code

```java
// UnixPathType.java
@Override
public ParseResult parsePath(String path) {
    if (path.isEmpty()) {
        return emptyPath();
    }

    checkValid(path); // remove call

    String root = path.startsWith("/") ? "/" : null;
    return new ParseResult(root, splitter().split(path));
}
```

```java
// UrlTest.java
@Test
public void creatUrl() throws MalformedURLException {
    URL url = path.toUri().toURL();
    assertThat(url).isNotNull();
}
```

##### results

```
mvn test -Dtest=UrlTest#creatUrl

[INFO] -------------------------------------------------------
[INFO]  T E S T S
[INFO] -------------------------------------------------------
[INFO] Running com.google.common.jimfs.UrlTest
[INFO] Tests run: 1, Failures: 0, Errors: 0, Skipped: 0, Time elapsed: 0.087 s -- in com.google.common.jimfs.UrlTest
[INFO] 
[INFO] Results:
[INFO] 
[INFO] Tests run: 1, Failures: 0, Errors: 0, Skipped: 0
[INFO] 
[INFO] ------------------------------------------------------------------------
```

```
mvn test -Dtest=ConfigurationTest#testFileSystemForDefaultOsXConfiguration

[INFO] -------------------------------------------------------
[INFO]  T E S T S
[INFO] -------------------------------------------------------
[INFO] Running com.google.common.jimfs.ConfigurationTest
[INFO] Tests run: 1, Failures: 0, Errors: 0, Skipped: 0, Time elapsed: 0.096 s -- in com.google.common.jimfs.ConfigurationTest
[INFO] 
[INFO] Results:
[INFO] 
[INFO] Tests run: 1, Failures: 0, Errors: 0, Skipped: 0
[INFO] 
[INFO] ------------------------------------------------------------------------
```

#### victim

##### code

```java
// UnixPathType.java
@Override
public ParseResult parsePath(String path) {
    if (path.isEmpty()) {
        return emptyPath();
    }

    checkValid(path);

    String root = path.startsWith("/") ? "/" : null; // negated conditional
    return new ParseResult(root, splitter().split(path));
}
```

##### results

```
mvn test -Dtest=UrlTest#creatUrl

[INFO] -------------------------------------------------------
[INFO]  T E S T S
[INFO] -------------------------------------------------------
[INFO] Running com.google.common.jimfs.UrlTest
[ERROR] Tests run: 1, Failures: 0, Errors: 1, Skipped: 0, Time elapsed: 0.044 s <<< FAILURE! -- in com.google.common.jimfs.UrlTest
[ERROR] com.google.common.jimfs.UrlTest.creatUrl -- Time elapsed: 0.014 s <<< ERROR!
java.lang.ExceptionInInitializerError
        at com.google.common.jimfs.Configuration.unix(Configuration.java:86)
        at com.google.common.jimfs.UrlTest.<init>(UrlTest.java:46)
        at java.base/jdk.internal.reflect.NativeConstructorAccessorImpl.newInstance0(Native Method)
        at java.base/jdk.internal.reflect.NativeConstructorAccessorImpl.newInstance(NativeConstructorAccessorImpl.java:77)
        at java.base/jdk.internal.reflect.DelegatingConstructorAccessorImpl.newInstance(DelegatingConstructorAccessorImpl.java:45)
        at java.base/java.lang.reflect.Constructor.newInstanceWithCaller(Constructor.java:500)
        at java.base/java.lang.reflect.Constructor.newInstance(Constructor.java:481)
        at org.junit.runners.BlockJUnit4ClassRunner.createTest(BlockJUnit4ClassRunner.java:250)
        at org.junit.runners.BlockJUnit4ClassRunner.createTest(BlockJUnit4ClassRunner.java:260)
        at org.junit.runners.BlockJUnit4ClassRunner$2.runReflectiveCall(BlockJUnit4ClassRunner.java:309)
        at org.junit.internal.runners.model.ReflectiveCallable.run(ReflectiveCallable.java:12)
        at org.junit.runners.BlockJUnit4ClassRunner.methodBlock(BlockJUnit4ClassRunner.java:306)
        at org.junit.runners.BlockJUnit4ClassRunner$1.evaluate(BlockJUnit4ClassRunner.java:100)
        at org.junit.runners.ParentRunner.runLeaf(ParentRunner.java:366)
        at org.junit.runners.BlockJUnit4ClassRunner.runChild(BlockJUnit4ClassRunner.java:103)
        at org.junit.runners.BlockJUnit4ClassRunner.runChild(BlockJUnit4ClassRunner.java:63)
        at org.junit.runners.ParentRunner$4.run(ParentRunner.java:331)
        at org.junit.runners.ParentRunner$1.schedule(ParentRunner.java:79)
        at org.junit.runners.ParentRunner.runChildren(ParentRunner.java:329)
        at org.junit.runners.ParentRunner.access$100(ParentRunner.java:66)
        at org.junit.runners.ParentRunner$2.evaluate(ParentRunner.java:293)
        at org.junit.runners.ParentRunner$3.evaluate(ParentRunner.java:306)
        at org.junit.runners.ParentRunner.run(ParentRunner.java:413)
        at org.apache.maven.surefire.junit4.JUnit4Provider.execute(JUnit4Provider.java:316)
        at org.apache.maven.surefire.junit4.JUnit4Provider.executeWithRerun(JUnit4Provider.java:240)
        at org.apache.maven.surefire.junit4.JUnit4Provider.executeTestSet(JUnit4Provider.java:214)
        at org.apache.maven.surefire.junit4.JUnit4Provider.invoke(JUnit4Provider.java:155)
        at org.apache.maven.surefire.booter.ForkedBooter.runSuitesInProcess(ForkedBooter.java:385)
        at org.apache.maven.surefire.booter.ForkedBooter.execute(ForkedBooter.java:162)
        at org.apache.maven.surefire.booter.ForkedBooter.run(ForkedBooter.java:507)
        at org.apache.maven.surefire.booter.ForkedBooter.main(ForkedBooter.java:495)
Caused by: java.lang.IllegalArgumentException: invalid root: /
        at com.google.common.base.Preconditions.checkArgument(Preconditions.java:220)
        at com.google.common.jimfs.Configuration$Builder.setRoots(Configuration.java:674)
        at com.google.common.jimfs.Configuration$UnixHolder.<clinit>(Configuration.java:93)
        ... 31 more

[INFO] 
[INFO] Results:
[INFO] 
[ERROR] Errors: 
[ERROR]   UrlTest.<init>:46 ? ExceptionInInitializer
[INFO] 
[ERROR] Tests run: 1, Failures: 0, Errors: 1, Skipped: 0
[INFO] 
[INFO] ------------------------------------------------------------------------
```

```
mvn test -Dtest=ConfigurationTest#testFileSystemForDefaultOsXConfiguration

[INFO] -------------------------------------------------------
[INFO]  T E S T S
[INFO] -------------------------------------------------------
[INFO] Running com.google.common.jimfs.ConfigurationTest
[ERROR] Tests run: 1, Failures: 0, Errors: 1, Skipped: 0, Time elapsed: 0.046 s <<< FAILURE! -- in com.google.common.jimfs.ConfigurationTest
[ERROR] com.google.common.jimfs.ConfigurationTest.testFileSystemForDefaultOsXConfiguration -- Time elapsed: 0.013 s <<< ERROR!
java.lang.ExceptionInInitializerError
        at com.google.common.jimfs.Configuration.unix(Configuration.java:86)
        at com.google.common.jimfs.Configuration$OsxHolder.<clinit>(Configuration.java:139)
        at com.google.common.jimfs.Configuration.osX(Configuration.java:134)
        at com.google.common.jimfs.ConfigurationTest.testFileSystemForDefaultOsXConfiguration(ConfigurationTest.java:113)
        at java.base/jdk.internal.reflect.NativeMethodAccessorImpl.invoke0(Native Method)
        at java.base/jdk.internal.reflect.NativeMethodAccessorImpl.invoke(NativeMethodAccessorImpl.java:77)
        at java.base/jdk.internal.reflect.DelegatingMethodAccessorImpl.invoke(DelegatingMethodAccessorImpl.java:43)
        at java.base/java.lang.reflect.Method.invoke(Method.java:569)
        at org.junit.runners.model.FrameworkMethod$1.runReflectiveCall(FrameworkMethod.java:59)
        at org.junit.internal.runners.model.ReflectiveCallable.run(ReflectiveCallable.java:12)
        at org.junit.runners.model.FrameworkMethod.invokeExplosively(FrameworkMethod.java:56)
        at org.junit.internal.runners.statements.InvokeMethod.evaluate(InvokeMethod.java:17)
        at org.junit.runners.ParentRunner$3.evaluate(ParentRunner.java:306)
        at org.junit.runners.BlockJUnit4ClassRunner$1.evaluate(BlockJUnit4ClassRunner.java:100)
        at org.junit.runners.ParentRunner.runLeaf(ParentRunner.java:366)
        at org.junit.runners.BlockJUnit4ClassRunner.runChild(BlockJUnit4ClassRunner.java:103)
        at org.junit.runners.BlockJUnit4ClassRunner.runChild(BlockJUnit4ClassRunner.java:63)
        at org.junit.runners.ParentRunner$4.run(ParentRunner.java:331)
        at org.junit.runners.ParentRunner$1.schedule(ParentRunner.java:79)
        at org.junit.runners.ParentRunner.runChildren(ParentRunner.java:329)
        at org.junit.runners.ParentRunner.access$100(ParentRunner.java:66)
        at org.junit.runners.ParentRunner$2.evaluate(ParentRunner.java:293)
        at org.junit.runners.ParentRunner$3.evaluate(ParentRunner.java:306)
        at org.junit.runners.ParentRunner.run(ParentRunner.java:413)
        at org.apache.maven.surefire.junit4.JUnit4Provider.execute(JUnit4Provider.java:316)
        at org.apache.maven.surefire.junit4.JUnit4Provider.executeWithRerun(JUnit4Provider.java:240)
        at org.apache.maven.surefire.junit4.JUnit4Provider.executeTestSet(JUnit4Provider.java:214)
        at org.apache.maven.surefire.junit4.JUnit4Provider.invoke(JUnit4Provider.java:155)
        at org.apache.maven.surefire.booter.ForkedBooter.runSuitesInProcess(ForkedBooter.java:385)
        at org.apache.maven.surefire.booter.ForkedBooter.execute(ForkedBooter.java:162)
        at org.apache.maven.surefire.booter.ForkedBooter.run(ForkedBooter.java:507)
        at org.apache.maven.surefire.booter.ForkedBooter.main(ForkedBooter.java:495)
Caused by: java.lang.IllegalArgumentException: invalid root: /
        at com.google.common.base.Preconditions.checkArgument(Preconditions.java:220)
        at com.google.common.jimfs.Configuration$Builder.setRoots(Configuration.java:674)
        at com.google.common.jimfs.Configuration$UnixHolder.<clinit>(Configuration.java:93)
        ... 32 more

[INFO] 
[INFO] Results:
[INFO] 
[ERROR] Errors: 
[ERROR]   ConfigurationTest.testFileSystemForDefaultOsXConfiguration:113 ? ExceptionInInitializer
[INFO] 
[ERROR] Tests run: 1, Failures: 0, Errors: 1, Skipped: 0
[INFO] 
[INFO] ------------------------------------------------------------------------
```

### 5076 (13) -- Survived

Run 13-jimfs_3-0-mid_8-0-mid.json, both fail.

Run 13-jimfs_3-0-mid_8-0-mid_dummy.json (polluted mutant did nothing), only victim exists and passes.

#### polluter

##### code

```java
// UnixPathType.java
@Override
public ParseResult parsePath(String path) {
    if (path.isEmpty()) {
        return emptyPath();
    }

    checkValid(path);

    String root = path.startsWith("/") ? "/" : null; // negated conditional
    return new ParseResult(root, splitter().split(path));
}
```

```java
// UrlTest.java
@Test
public void creatUrl() throws MalformedURLException {
    URL url = path.toUri().toURL();
    assertThat(url).isNotNull();
}
```

##### results

The same as 4996's victim results.

#### victim

##### code

```java
// UnixPathType.java
@Override
public String toString(@Nullable String root, Iterable<String> names) {
    StringBuilder builder = new StringBuilder();
    if (root != null) { // change != to ==
      builder.append(root);
    }
    joiner().appendTo(builder, names);
    return builder.toString();
}
```

##### results

```
mvn test -Dtest=UrlTest#creatUrl

[INFO] -------------------------------------------------------
[INFO]  T E S T S
[INFO] -------------------------------------------------------
[INFO] Running com.google.common.jimfs.UrlTest
[INFO] Tests run: 1, Failures: 0, Errors: 0, Skipped: 0, Time elapsed: 0.096 s -- in com.google.common.jimfs.UrlTest
[INFO] 
[INFO] Results:
[INFO] 
[INFO] Tests run: 1, Failures: 0, Errors: 0, Skipped: 0
[INFO] 
[INFO] ------------------------------------------------------------------------
```

```
mvn test -Dtest=ConfigurationTest#testFileSystemForDefaultOsXConfiguration

[INFO] -------------------------------------------------------
[INFO]  T E S T S
[INFO] -------------------------------------------------------
[INFO] Running com.google.common.jimfs.ConfigurationTest
[INFO] Tests run: 1, Failures: 0, Errors: 0, Skipped: 0, Time elapsed: 0.098 s -- in com.google.common.jimfs.ConfigurationTest
[INFO] 
[INFO] Results:
[INFO] 
[INFO] Tests run: 1, Failures: 0, Errors: 0, Skipped: 0
[INFO] 
[INFO] ------------------------------------------------------------------------
```

### 5107 (14) -- Survived

Run 14-jimfs_3-0-mid_8-0-edge.json, both fail.

Run 14-jimfs_3-0-mid_8-0-edge_dummy.json (polluted mutant did nothing), both pass.

#### polluter

##### code

```java
// UnixPathType.java
@Override
public ParseResult parsePath(String path) {
    if (path.isEmpty()) {
        return emptyPath();
    }

    checkValid(path);

    String root = path.startsWith("/") ? "/" : null;
    return new ParseResult(root, splitter().split(path)); // return null
}
```

```java
// UrlTest.java
@Test
public void creatUrl() throws MalformedURLException {
    URL url = path.toUri().toURL();
    assertThat(url).isNotNull();
}
```

##### results

```
mvn test -Dtest=UrlTest#creatUrl

[INFO] -------------------------------------------------------
[INFO]  T E S T S
[INFO] -------------------------------------------------------
[INFO] Running com.google.common.jimfs.UrlTest
[ERROR] Tests run: 1, Failures: 0, Errors: 1, Skipped: 0, Time elapsed: 0.045 s <<< FAILURE! -- in com.google.common.jimfs.UrlTest
[ERROR] com.google.common.jimfs.UrlTest.creatUrl -- Time elapsed: 0.013 s <<< ERROR!
java.lang.ExceptionInInitializerError
        at com.google.common.jimfs.Configuration.unix(Configuration.java:86)
        at com.google.common.jimfs.UrlTest.<init>(UrlTest.java:46)
        at java.base/jdk.internal.reflect.NativeConstructorAccessorImpl.newInstance0(Native Method)
        at java.base/jdk.internal.reflect.NativeConstructorAccessorImpl.newInstance(NativeConstructorAccessorImpl.java:77)
        at java.base/jdk.internal.reflect.DelegatingConstructorAccessorImpl.newInstance(DelegatingConstructorAccessorImpl.java:45)
        at java.base/java.lang.reflect.Constructor.newInstanceWithCaller(Constructor.java:500)
        at java.base/java.lang.reflect.Constructor.newInstance(Constructor.java:481)
        at org.junit.runners.BlockJUnit4ClassRunner.createTest(BlockJUnit4ClassRunner.java:250)
        at org.junit.runners.BlockJUnit4ClassRunner.createTest(BlockJUnit4ClassRunner.java:260)
        at org.junit.runners.BlockJUnit4ClassRunner$2.runReflectiveCall(BlockJUnit4ClassRunner.java:309)
        at org.junit.internal.runners.model.ReflectiveCallable.run(ReflectiveCallable.java:12)
        at org.junit.runners.BlockJUnit4ClassRunner.methodBlock(BlockJUnit4ClassRunner.java:306)
        at org.junit.runners.BlockJUnit4ClassRunner$1.evaluate(BlockJUnit4ClassRunner.java:100)
        at org.junit.runners.ParentRunner.runLeaf(ParentRunner.java:366)
        at org.junit.runners.BlockJUnit4ClassRunner.runChild(BlockJUnit4ClassRunner.java:103)
        at org.junit.runners.BlockJUnit4ClassRunner.runChild(BlockJUnit4ClassRunner.java:63)
        at org.junit.runners.ParentRunner$4.run(ParentRunner.java:331)
        at org.junit.runners.ParentRunner$1.schedule(ParentRunner.java:79)
        at org.junit.runners.ParentRunner.runChildren(ParentRunner.java:329)
        at org.junit.runners.ParentRunner.access$100(ParentRunner.java:66)
        at org.junit.runners.ParentRunner$2.evaluate(ParentRunner.java:293)
        at org.junit.runners.ParentRunner$3.evaluate(ParentRunner.java:306)
        at org.junit.runners.ParentRunner.run(ParentRunner.java:413)
        at org.apache.maven.surefire.junit4.JUnit4Provider.execute(JUnit4Provider.java:316)
        at org.apache.maven.surefire.junit4.JUnit4Provider.executeWithRerun(JUnit4Provider.java:240)
        at org.apache.maven.surefire.junit4.JUnit4Provider.executeTestSet(JUnit4Provider.java:214)
        at org.apache.maven.surefire.junit4.JUnit4Provider.invoke(JUnit4Provider.java:155)
        at org.apache.maven.surefire.booter.ForkedBooter.runSuitesInProcess(ForkedBooter.java:385)
        at org.apache.maven.surefire.booter.ForkedBooter.execute(ForkedBooter.java:162)
        at org.apache.maven.surefire.booter.ForkedBooter.run(ForkedBooter.java:507)
        at org.apache.maven.surefire.booter.ForkedBooter.main(ForkedBooter.java:495)
Caused by: java.lang.NullPointerException: Cannot invoke "com.google.common.jimfs.PathType$ParseResult.isRoot()" because "parseResult" is null
        at com.google.common.jimfs.Configuration$Builder.setRoots(Configuration.java:674)
        at com.google.common.jimfs.Configuration$UnixHolder.<clinit>(Configuration.java:93)
        ... 31 more

[INFO] 
[INFO] Results:
[INFO] 
[ERROR] Errors: 
[ERROR]   UrlTest.<init>:46 ? ExceptionInInitializer
[INFO] 
[ERROR] Tests run: 1, Failures: 0, Errors: 1, Skipped: 0
[INFO] 
[INFO] ------------------------------------------------------------------------
```

```
mvn test -Dtest=ConfigurationTest#testFileSystemForDefaultOsXConfiguration

[INFO] -------------------------------------------------------
[INFO]  T E S T S
[INFO] -------------------------------------------------------
[INFO] Running com.google.common.jimfs.ConfigurationTest
[ERROR] Tests run: 1, Failures: 0, Errors: 1, Skipped: 0, Time elapsed: 0.045 s <<< FAILURE! -- in com.google.common.jimfs.ConfigurationTest
[ERROR] com.google.common.jimfs.ConfigurationTest.testFileSystemForDefaultOsXConfiguration -- Time elapsed: 0.012 s <<< ERROR!
java.lang.ExceptionInInitializerError
        at com.google.common.jimfs.Configuration.unix(Configuration.java:86)
        at com.google.common.jimfs.Configuration$OsxHolder.<clinit>(Configuration.java:139)
        at com.google.common.jimfs.Configuration.osX(Configuration.java:134)
        at com.google.common.jimfs.ConfigurationTest.testFileSystemForDefaultOsXConfiguration(ConfigurationTest.java:113)
        at java.base/jdk.internal.reflect.NativeMethodAccessorImpl.invoke0(Native Method)
        at java.base/jdk.internal.reflect.NativeMethodAccessorImpl.invoke(NativeMethodAccessorImpl.java:77)
        at java.base/jdk.internal.reflect.DelegatingMethodAccessorImpl.invoke(DelegatingMethodAccessorImpl.java:43)
        at java.base/java.lang.reflect.Method.invoke(Method.java:569)
        at org.junit.runners.model.FrameworkMethod$1.runReflectiveCall(FrameworkMethod.java:59)
        at org.junit.internal.runners.model.ReflectiveCallable.run(ReflectiveCallable.java:12)
        at org.junit.runners.model.FrameworkMethod.invokeExplosively(FrameworkMethod.java:56)
        at org.junit.internal.runners.statements.InvokeMethod.evaluate(InvokeMethod.java:17)
        at org.junit.runners.ParentRunner$3.evaluate(ParentRunner.java:306)
        at org.junit.runners.BlockJUnit4ClassRunner$1.evaluate(BlockJUnit4ClassRunner.java:100)
        at org.junit.runners.ParentRunner.runLeaf(ParentRunner.java:366)
        at org.junit.runners.BlockJUnit4ClassRunner.runChild(BlockJUnit4ClassRunner.java:103)
        at org.junit.runners.BlockJUnit4ClassRunner.runChild(BlockJUnit4ClassRunner.java:63)
        at org.junit.runners.ParentRunner$4.run(ParentRunner.java:331)
        at org.junit.runners.ParentRunner$1.schedule(ParentRunner.java:79)
        at org.junit.runners.ParentRunner.runChildren(ParentRunner.java:329)
        at org.junit.runners.ParentRunner.access$100(ParentRunner.java:66)
        at org.junit.runners.ParentRunner$2.evaluate(ParentRunner.java:293)
        at org.junit.runners.ParentRunner$3.evaluate(ParentRunner.java:306)
        at org.junit.runners.ParentRunner.run(ParentRunner.java:413)
        at org.apache.maven.surefire.junit4.JUnit4Provider.execute(JUnit4Provider.java:316)
        at org.apache.maven.surefire.junit4.JUnit4Provider.executeWithRerun(JUnit4Provider.java:240)
        at org.apache.maven.surefire.junit4.JUnit4Provider.executeTestSet(JUnit4Provider.java:214)
        at org.apache.maven.surefire.junit4.JUnit4Provider.invoke(JUnit4Provider.java:155)
        at org.apache.maven.surefire.booter.ForkedBooter.runSuitesInProcess(ForkedBooter.java:385)
        at org.apache.maven.surefire.booter.ForkedBooter.execute(ForkedBooter.java:162)
        at org.apache.maven.surefire.booter.ForkedBooter.run(ForkedBooter.java:507)
        at org.apache.maven.surefire.booter.ForkedBooter.main(ForkedBooter.java:495)
Caused by: java.lang.NullPointerException: Cannot invoke "com.google.common.jimfs.PathType$ParseResult.isRoot()" because "parseResult" is null
        at com.google.common.jimfs.Configuration$Builder.setRoots(Configuration.java:674)
        at com.google.common.jimfs.Configuration$UnixHolder.<clinit>(Configuration.java:93)
        ... 32 more

[INFO] 
[INFO] Results:
[INFO] 
[ERROR] Errors: 
[ERROR]   ConfigurationTest.testFileSystemForDefaultOsXConfiguration:113 ? ExceptionInInitializer
[INFO] 
[ERROR] Tests run: 1, Failures: 0, Errors: 1, Skipped: 0
[INFO] 
[INFO] ------------------------------------------------------------------------
```

#### victim

##### code

```java
// UnixPathType.java
@Override
public String toString(@Nullable String root, Iterable<String> names) {
    StringBuilder builder = new StringBuilder();
    if (root != null) {
      builder.append(root);
    }
    joiner().appendTo(builder, names);
    return builder.toString(); // return new String();
}
```

##### results

```
mvn test -Dtest=UrlTest#creatUrl

[INFO] -------------------------------------------------------
[INFO]  T E S T S
[INFO] -------------------------------------------------------
[INFO] Running com.google.common.jimfs.UrlTest
[INFO] Tests run: 1, Failures: 0, Errors: 0, Skipped: 0, Time elapsed: 0.088 s -- in com.google.common.jimfs.UrlTest
[INFO] 
[INFO] Results:
[INFO] 
[INFO] Tests run: 1, Failures: 0, Errors: 0, Skipped: 0
[INFO] 
[INFO] ------------------------------------------------------------------------
```

```
mvn test -Dtest=ConfigurationTest#testFileSystemForDefaultOsXConfiguration

[INFO] -------------------------------------------------------
[INFO]  T E S T S
[INFO] -------------------------------------------------------
[INFO] Running com.google.common.jimfs.ConfigurationTest
[INFO] Tests run: 1, Failures: 0, Errors: 0, Skipped: 0, Time elapsed: 0.096 s -- in com.google.common.jimfs.ConfigurationTest
[INFO] 
[INFO] Results:
[INFO] 
[INFO] Tests run: 1, Failures: 0, Errors: 0, Skipped: 0
[INFO] 
[INFO] ------------------------------------------------------------------------
```
