 import org.sosy_lab.sv_benchmarks.Verifier;
 public class StaticCharMethods04 {
 public static void main(String[] args) {
         char c = Verifier.nondetChar();
         assert Character.isLetter(c);
    }
 }