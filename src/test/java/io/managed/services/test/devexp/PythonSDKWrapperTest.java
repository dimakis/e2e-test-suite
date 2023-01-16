package io.managed.services.test.devexp;

import com.openshift.cloud.api.kas.auth.models.Record;
import com.openshift.cloud.api.kas.models.KafkaRequest;
import io.managed.services.test.Environment;
import io.managed.services.test.cli.CliGenericException;
import io.managed.services.test.pythonSDKWrapper.PythonSDKWrapper;
import io.managed.services.test.pythonSDKWrapper.kafkamgmt.utils.SDKUtils;
import lombok.SneakyThrows;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.testng.annotations.BeforeClass;
import org.testng.annotations.Test;

import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Arrays;
import java.util.List;
import java.util.Objects;
import java.util.Optional;

import static org.testng.Assert.*;


/**
 * Test the application services CLI[1] kafka commands.
 * <p>
 * The tests download the CLI from GitHub to the local machine where the test suite is running
 * and perform all operations using the CLI.
 * <p>
 * By default the latest version of the CLI is downloaded otherwise a specific version can be set using
 * the CLI_VERSION env. The CLI platform (linux, mac, win) and arch (amd64, arm) is automatically detected,
 * or it can be enforced using the CLI_PLATFORM and CLI_ARCH env.
 * <p>
 * 1. https://github.com/redhat-developer/app-services-cli
 * <p>
 * <b>Requires:</b>
 * <ul>
 *     <li> PRIMARY_USERNAME
 *     <li> PRIMARY_PASSWORD
 * </ul>
 */
@Test
public class PythonSDKWrapperTest {
    private static final Logger LOGGER = LogManager.getLogger(KafkaCLITest.class);

    private static final String KAFKA_INSTANCE_NAME = "sdk-e2e-test-instance-" + Environment.LAUNCH_KEY;

    private static final String SERVICE_ACCOUNT_NAME = "sdk-e2e-service-account-" + Environment.LAUNCH_KEY;

    private static final String TOPIC_NAME = "sdk-e2e-test-topic";
    private static final String TOPIC_NAME_PRODUCE_CONSUME = "produce-consume-test-topic";
    private static final int DEFAULT_PARTITIONS = 1;

    private PythonSDKWrapper pythonSDK;

    private KafkaRequest kafka;

    @BeforeClass
    public void bootstrap() {
        assertNotNull(Environment.OFFLINE_TOKEN, "the OFFLINE_TOKEN env is null");
        Path userDirectory = Paths.get("")
                .toAbsolutePath();
        this.pythonSDK = new PythonSDKWrapper(userDirectory);
    }


    @Test()
    @SneakyThrows
    public void testCreateKafkaInstance() {

        LOGGER.info("create kafka instance with name {}", KAFKA_INSTANCE_NAME);
        var k = pythonSDK.createKafka(KAFKA_INSTANCE_NAME, Environment.CLOUD_PROVIDER, Environment.DEFAULT_KAFKA_REGION, Environment.SDK_PLAN);
        LOGGER.debug(k);

        LOGGER.info("wait for kafka instance: {}", k.getId());
        kafka = SDKUtils.waitUntilKafkaIsReady(pythonSDK, k.getId());
        LOGGER.debug(kafka);
    }

    @SneakyThrows
    public void testListKafkaInstances() {

        var list = pythonSDK.listKafka();
        LOGGER.debug(list);

        var exists = list.getItems().stream()
                .filter(k -> KAFKA_INSTANCE_NAME.equals(k.getName()))
                .findAny();
        assertTrue(exists.isPresent());
    }

    @SneakyThrows
    public void testCreateServiceAccount() {
        LOGGER.info("creating service account with name: {}", SERVICE_ACCOUNT_NAME);
        var serviceAccount = pythonSDK.createServiceAccount(SERVICE_ACCOUNT_NAME);

        var exists = Arrays.stream(pythonSDK.listServiceAccounts())
                .filter(sa -> SERVICE_ACCOUNT_NAME.equals(sa.getName()))
                .findAny();
        assertTrue(exists.isPresent());
    }

    @SneakyThrows
    public void testGetServiceAccounts() {
        LOGGER.info("getting service accounts");
        var serviceAccounts = pythonSDK.listServiceAccounts();

        var exists = Arrays.stream(serviceAccounts)
                .filter(sa -> SERVICE_ACCOUNT_NAME.equals(sa.getName()))
                .findAny();
        assertTrue(exists.isPresent());
    }


    @Test(dependsOnMethods = "testCreateKafkaInstance", enabled = true)
    @SneakyThrows
    public void testCreateTopic() {

        LOGGER.info("create kafka topic with name {}", KAFKA_INSTANCE_NAME);
        var topic = pythonSDK.createTopic(kafka.getId(), TOPIC_NAME);
        LOGGER.debug(topic);

        assertEquals(topic.getName(), TOPIC_NAME);

//         this checks partition size
        assertEquals(Objects.requireNonNull(topic.getPartitions()).size(), DEFAULT_PARTITIONS);
    }


    @Test(dependsOnMethods = {"testCreateKafkaInstance", "testGrantProducerAndConsumerAccess"}, enabled = true)
    @SneakyThrows
    public void testProducePlainMessages() {
        var messages = List.of("First message", "Second message", "Third message");

        LOGGER.info("produce messages");
        int i = 0;
        for (String message : messages) {
            // produce single message
            LOGGER.info("Produce message '{}'", message);
            Record record = pythonSDK.produceRecords(TOPIC_NAME, kafka.getId(), message);
            LOGGER.debug(record);

            assertEquals(record.getValue(), message);
            assertEquals(Optional.ofNullable(record.getOffset()), i++);
        }
    }

    //     this test is not passing due to a bug in the python sdk as documented in the list_topics.py filw
//    @Test(dependsOnMethods = "testCreateTopic", enabled = true)
//    @SneakyThrows
//    public void testListTopics() {
//
//        var list = pythonSDK.listTopics();
//        LOGGER.debug(list);
//
//        var exists = Objects.requireNonNull(list.getItems()).stream()
//                .filter(t -> TOPIC_NAME.equals(t.getName()))
//                .findAny();
//        assertTrue(exists.isPresent());
//    }

    // currently not working due to a bug in the python sdk
    //     @Test(dependsOnMethods = {"testProduceCustomMessage"}, enabled = true)
//    @SneakyThrows
//    public void testConsumeCustomMessage() {
//        LOGGER.info("consuming all messages from partition '1' topic '{}'", TOPIC_NAME);
//        List<Record> consumedRecords = pythonSDK.consumeRecords(TOPIC_NAME, kafka.getId(), 0, 1);
//
//        Record consumedRecord = consumedRecords.get(0);
//        LOGGER.debug(consumedRecord);
//        assertEquals(String.valueOf(consumedRecord.getPartition()), 1, "failed to read partition 1");
//        assertEquals(consumedRecord.getKey(), customRecordKey, "failed to obtain expected key");
//    }


    @SneakyThrows
    public void testDeleteTopic() {

        LOGGER.info("delete topic '{}'", TOPIC_NAME);
        pythonSDK.deleteTopic(kafka.getId(), TOPIC_NAME);

        assertThrows(CliGenericException.class,
                () -> pythonSDK.describeTopic(TOPIC_NAME));
    }

    @SneakyThrows
    public void testDeleteServiceAccount() {
        LOGGER.info("deleting service account with name: {}", SERVICE_ACCOUNT_NAME);
        pythonSDK.deleteServiceAccount(SERVICE_ACCOUNT_NAME);

        var exists = Arrays.stream(pythonSDK.listServiceAccounts())
                .filter(sa -> SERVICE_ACCOUNT_NAME.equals(sa.getName()))
                .findAny();
        assertTrue(exists.isEmpty());
    }

    @Test(dependsOnMethods = "testCreateKafkaInstance", priority = 3, enabled = true)
    @SneakyThrows
    public void testDeleteKafkaInstance() {

        LOGGER.info("delete kafka instance '{}'", kafka.getId());
        pythonSDK.deleteKafka(kafka.getId());

        SDKUtils.waitUntilKafkaIsDeleted(pythonSDK, kafka.getId());
    }
}
