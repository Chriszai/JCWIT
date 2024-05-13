import org.sosy_lab.sv_benchmarks.Verifier; import Components.MethodCallMonitor;

public class Test {
    public static void main(String[] args) {
        int c = 4; assert c == 4; assert c == 4;
        Linked.add();
        Verifier.nondetBoolean();
    }
}

class Linked {
  public static int add() {
      Linked linked = new Linked(); MethodCallMonitor.assertionImplementation(MethodCallMonitor.Linked_add__I, new Linked() instanceof Linked, linked instanceof Linked);
      int c = 5; MethodCallMonitor.assertionImplementation(MethodCallMonitor.Linked_add__I, c == 5);
      return 4;
  }
}
