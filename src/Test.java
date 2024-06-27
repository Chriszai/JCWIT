import org.sosy_lab.sv_benchmarks.Verifier; import Components.MethodCallMonitor;

class Test {
    static void isRightTriangle(int a, int b, int c){
       int x;
       if(a > b && a > c){
           x = a * a; MethodCallMonitor.assertionImplementation(MethodCallMonitor.Test_7 ++, x == 25, x == 100);
       } else if (b > a && b > c) {
           x = b * b;
       } else x = c * c;
       int y = a * a + b * b + c * c; MethodCallMonitor.assertionImplementation(MethodCallMonitor.Test_11 ++, y == 50, y == 200);
       if(2 * x == y){
           assert true;
       }
       else assert false;
    }
    public static void main(String[] args) {
       isRightTriangle(5,4,3);
       isRightTriangle(10,8,6);
    }
}