import org.sosy_lab.sv_benchmarks.Verifier;

public class stringTest {
  public static void main(String[] args) {
    StringBuilder buffer = new StringBuilder(Verifier.nondetString());
    assert buffer.charAt(0) == buffer.charAt(4);
  }
}