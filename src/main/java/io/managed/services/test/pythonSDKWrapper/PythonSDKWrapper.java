package io.managed.services.test.pythonSDKWrapper;

import com.openshift.cloud.api.kas.auth.models.AclBindingListPage;
import com.openshift.cloud.api.kas.auth.models.Record;
import com.openshift.cloud.api.kas.auth.models.Topic;
import com.openshift.cloud.api.kas.auth.models.TopicsList;
import com.openshift.cloud.api.kas.models.KafkaRequest;
import com.openshift.cloud.api.kas.models.KafkaRequestList;
import com.openshift.cloud.api.serviceaccounts.models.ServiceAccountData;
import io.managed.services.test.RetryUtils;
import io.managed.services.test.ThrowingSupplier;
import io.managed.services.test.cli.AsyncProcess;
import io.managed.services.test.cli.CliGenericException;
import io.managed.services.test.cli.ProcessException;
import lombok.extern.log4j.Log4j2;
import org.testng.Assert;

import java.io.BufferedReader;
import java.io.File;
import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.file.Path;
import java.time.Duration;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.ExecutionException;

import static java.time.Duration.ofMinutes;
import static lombok.Lombok.sneakyThrow;

@Log4j2
public class PythonSDKWrapper {

    private static final Duration DEFAULT_TIMEOUT = ofMinutes(3);

    private static final String CLUSTER_CAPACITY_EXHAUSTED_CODE = "KAFKAS-MGMT-24";

    private final String workdir;
    private final String cmd;


    private final String pythonSDKPath = "e2e-test-suite/src/main/java/io/managed/services/test/pythonSDKWrapper/";

    public String FindPythonSDK() {
        String[] whichCmd = new String[]{"which", "python"};
        Process p = null;
        try {
            p = Runtime.getRuntime().exec(whichCmd);
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
        BufferedReader reader = new BufferedReader(new InputStreamReader(p.getInputStream()));
        String pythonExecutable;
        try {
            pythonExecutable = reader.readLine();
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
        return pythonExecutable;
    }

    public PythonSDKWrapper(Path path) {
        this.workdir = path.getParent().toString();
        this.cmd = FindPythonSDK();
    }

    public String getWorkdir() {
        return this.workdir;
    }

    private ProcessBuilder builder(List<String> command) {
        var cmd = new ArrayList<String>();
        cmd.add(this.cmd);
        cmd.addAll(command);


        return new ProcessBuilder(cmd)
                .directory(new File(workdir));
    }

    private AsyncProcess exec(String... command) throws CliGenericException {
        return exec(List.of(command));
    }

    private AsyncProcess exec(List<String> command) throws CliGenericException {
        try {
            return execAsync(command).sync(DEFAULT_TIMEOUT);
        } catch (ProcessException e) {
            throw CliGenericException.exception(e);
        }
    }

    private AsyncProcess execAsync(String... command) {
        return execAsync(List.of(command));
    }

    private AsyncProcess execAsync(List<String> command) {
        try {
            return new AsyncProcess(builder(command).start());
        } catch (IOException e) {
            throw sneakyThrow(e);
        }
    }


    public KafkaRequest createKafka(String name, String cloudProvider, String region, String plan) throws CliGenericException {
        System.out.println("workdir==" + getWorkdir());
        return retryKafkaCreation(() -> exec(pythonSDKPath + "kafkamgmt/create_kafka.py", "--kafka_name", name, "--cloud_provider", cloudProvider, "--region", region, "--plan", plan))
                .asJson(KafkaRequest.class);
    }

    public void deleteKafka(String id) throws CliGenericException {
        retry(() -> exec(pythonSDKPath + "kafkamgmt/delete_kafka_by_id.py", "--kafka_id", id));
    }

    public KafkaRequest describeKafka(String id) throws CliGenericException {
        var kr = retry(() -> exec(pythonSDKPath + "kafkamgmt/describe_kafka.py", "--kafka_id", id));
        System.out.println("kr==" + kr);
        return kr.asJson(KafkaRequest.class);
    }

    public KafkaRequestList listKafka() throws CliGenericException {
        return retry(() -> exec(pythonSDKPath + "kafkamgmt/list_kafkas.py"))
                .asJson(KafkaRequestList.class);
    }

    public ServiceAccountData createServiceAccount(String name) throws CliGenericException {
        return retry(() -> exec(pythonSDKPath + "serviceaccount/create_service_account.py", "--service_account_name", name, "--service_account_description", "this is a description"))
                .asJson(ServiceAccountData.class);
    }

    public ServiceAccountData describeServiceAccount(String id) throws CliGenericException {
        return retry(() -> exec("service-account", "describe", "--id", id))
                .asJson(ServiceAccountData.class);
    }

    public ServiceAccountData[] listServiceAccounts() throws CliGenericException {
        return retry(() -> exec(pythonSDKPath + "serviceaccount/get_service_accounts.py"))
                .asJson(ServiceAccountData[].class);
    }

    public void deleteServiceAccount(String id) throws CliGenericException {
        retry(() -> exec(pythonSDKPath + "serviceaccount/delete_service_account.py", "--service_account_id", id));
    }

    public Topic createTopic(String kafkaId, String topicName) throws CliGenericException {
        var topic = retry(() -> exec(pythonSDKPath + "kafkaadmin/create_topic.py", "--kafka_id", kafkaId, "--topic_name", topicName));
        return topic.asJson(Topic.class);
    }

    public Topic createTopic(String kafkaId, String topicName, int partitions) throws CliGenericException {
        return retry(() -> exec(pythonSDKPath + "kafkaadmin/create_topic.py", "--kafka_id", kafkaId, "--topic_name", topicName, "--name", topicName, "--partitions", String.valueOf(partitions), "-o", "json"))
                .asJson(Topic.class);
    }

    public void deleteTopic(String kafkaId, String topicName) throws CliGenericException {
        retry(() -> exec(pythonSDKPath + "kafkaadmin/delete_topic.py", "--kafka_id", kafkaId, "--topic_name",  topicName));
    }

    public TopicsList listTopics() throws CliGenericException {
        return retry(() -> exec(pythonSDKPath + "kafkaadmin/list_topics.py"))
                .asJson(TopicsList.class);
    }

    public Topic describeTopic(String topicName) throws CliGenericException {
        return retry(() -> exec(pythonSDKPath + "kafkaadmin/get_topic.py", "--topic_name", topicName))
                .asJson(Topic.class);
    }

    public void grantProducerAndConsumerAccess(String kafkaId, String principalId) throws CliGenericException {
        retry(() -> exec(pythonSDKPath + "kafkaadmin/create_acl.py", "--kafka_id", kafkaId, "--principal", principalId, "--resource_type", "TOPIC", "--resource_name", "resourceName", "--pattern_type", "PREFIXED", "--operation_type", "ALLOW"));
    }

    public AclBindingListPage listACLs(String kafkaId) throws CliGenericException {
        return retry(() -> exec(pythonSDKPath + "kafkaadmin/getacls.py", "--kafka_id", kafkaId))
                .asJson(AclBindingListPage.class);
    }
    public void updateTopic(String topicName, String retentionTime) throws CliGenericException {
        retry(() -> exec(pythonSDKPath + "kafkaadmin/update_topic.py", "--name", topicName, "--retention-ms", retentionTime));
    }


    public Record produceRecords(String topicName, String instanceId, String message)
            throws IOException, ExecutionException, InterruptedException {
        List<String> cmd = List.of(pythonSDKPath + "kafkaadmin/produce_record.py", "--kafka_id", instanceId,
                "--topic_name", topicName,
                "--record_value", message
        );
        return produceRecords(message, cmd);
    }

    private Record produceRecords(String message, List<String> commands) throws IOException, ExecutionException, InterruptedException {
        var produceMessageProcess = execAsync(commands);
        var stdin = produceMessageProcess.stdin();

        // write message
        stdin.write(message);
        stdin.close();

        // return code
        var returnedCode = produceMessageProcess.future(Duration.ofSeconds(10)).get().waitFor();

        // Read Record object
        Record producedRecord = produceMessageProcess.asJson(Record.class);

        // Assert correctness
        Assert.assertEquals(returnedCode, 0);

        return producedRecord;
    }

    private <T, E extends Throwable> T retry(ThrowingSupplier<T, E> call) throws E {
        return RetryUtils.retry(1, call, PythonSDKWrapper::retryCondition);
    }

    private <T, E extends Throwable> T retryKafkaCreation(ThrowingSupplier<T, E> call) throws E {
        return RetryUtils.retry(
                1, null, call, PythonSDKWrapper::retryConditionKafkaCreation, 12, Duration.ofSeconds(10));
    }

    private static boolean retryConditionKafkaCreation(Throwable t) {
        if (t instanceof CliGenericException) {
            // quota problem,
            if (((CliGenericException) t).getCode() == 403 && ((CliGenericException) t).getMessage().contains(CLUSTER_CAPACITY_EXHAUSTED_CODE)) {
                return true;
            }
            // server side problem
            return ((CliGenericException) t).getCode() >= 500 && ((CliGenericException) t).getCode() < 600;
        }
        return false;
    }

    private static boolean retryCondition(Throwable t) {
        if (t instanceof CliGenericException) {
            return ((CliGenericException) t).getCode() >= 500 && ((CliGenericException) t).getCode() < 600;
        }
        return false;
    }

}
