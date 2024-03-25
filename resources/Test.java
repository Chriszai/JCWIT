import java.util.ArrayList;

public class Test {
    public static void main(String[] args) {
        Linked t1 = new Linked(); assert new Linked() instanceof Linked; assert t1 instanceof Linked;
        Linked t2 = new Linked(); assert new Linked() instanceof Linked; assert t2 instanceof Linked;
        t2.Value = 7; assert t2.Value == 7;
        t1.Next = new Linked(); assert t1.Next instanceof Linked;
        t1.Value = t2.Value + 4; assert t1.Value == 11;
        float k = 4.0f; assert k == 4.0;
    }
}

class Linked {
  public Linked Next;
  public int Value;
}
