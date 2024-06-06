import org.sosy_lab.sv_benchmarks.Verifier;

class Test {
    static void isRightTriangle(int a, int b, int c){
       int x;
       if(a > b && a > c){
           x = a * a;
       } else if (b > a && b > c) {
           x = b * b;
       } else x = c * c;
       int y = a * a + b * b + c * c;
       if(2 * x == y){
           assert true;
       }
       else assert false;
    }

    public static void main(String[] args) {
       isRightTriangle(5,4,3);
    }
}