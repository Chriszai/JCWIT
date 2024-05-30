import org.sosy_lab.sv_benchmarks.Verifier; import Components.MethodCallMonitor;


class Test {
    static void isRightTriangle(int a, int b, int c){
       int x;
       if(a > b && a > c){
           x = a * a; MethodCallMonitor.assertionImplementation(MethodCallMonitor.Test_isRightTriangle_III_V, x == 25);
       } else if (b > a && b > c) {
           x = b * b;
       } else x = c * c;
       int y = a * a + b * b + c * c; MethodCallMonitor.assertionImplementation(MethodCallMonitor.Test_isRightTriangle_III_V, y == 50);
       if(2 * x == y){
           assert true;
       }
       else assert false;
    }

    public static void main(String[] args) {
       isRightTriangle(5,4,3); MethodCallMonitor.Test_isRightTriangle_III_V ++;
    }
}