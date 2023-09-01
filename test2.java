import org.sosy_lab.sv_benchmarks.Verifier;
import utils.NewRandom;
import utils.TestSet;
public class test2 {

    public static Verifier verifier = new Verifier();
    public static TestSet testSet = new TestSet();

    public static void main(String[] args) {

        // int randomInt = verifier.nondetInt(testSet.intSet[1]);
        int randomInt = verifier.nondetInt();
        if (randomInt >= 10000) assert randomInt >= 10000 : "randomInt is greater 10000 ";
        
    }
}
