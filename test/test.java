import org.sosy_lab.sv_benchmarks.Verifier;

public class test {
  public static void main(String[] args) {
    String arg = Verifier.nondetString();

    StringBuilder buffer = new StringBuilder(arg);
    buffer.setCharAt(0, 'H');
    buffer.setCharAt(6, 'T');
    assert buffer.toString().equals("HiffBllTe Limited");
  }
}