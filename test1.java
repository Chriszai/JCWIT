import org.sosy_lab.sv_benchmarks.Verifier;

import java.util.Random;


public class test1 {
    public static Verifier verifier = new Verifier();
    long x = System.currentTimeMillis();

    public static void main(String[] args) {

        int i = new Random(11).nextInt();
        int r = 3;
        System.out.println(i);
//        if(x >= 1000l) assert x >= 1000 : "x is greater 1000";
    }
}
