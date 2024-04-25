import org.sosy_lab.sv_benchmarks.Verifier;

public class Test {
    public static void main(String[] args) {
        int c = 4; assert c == 4;
        Linked.add();
        Verifier.nondetBoolean();
    }
}

class Linked {
  public static int add() {
      Linked linked = new Linked();
      int c = 5;
      return 4;
  }
}
