import org.sosy_lab.sv_benchmarks.Verifier;

public class test {
    public static void main(String[] args) {
        int i = 10;

        for (int j = 0; j < 1; j++) {
            String v = Verifier.nondetString();
            System.out.println(v);
        }

        if (i >= 30) assert i >= 20 : "my super assertion"; // should hold
        
    }
}
