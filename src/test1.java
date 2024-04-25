import static java.lang.Math.max; import Components.MethodCallMonitor;

public class test1 {
    public static void main(String[] args) {
        isTriangle(3,4,5); MethodCallMonitor.test1_isTriangle_III_V ++;
        isTriangle(6,8,10); MethodCallMonitor.test1_isTriangle_III_V ++;
    }
    static void isTriangle(int a, int b, int c){
        int z = max(max(a,b),c);
        int result = a * a + b * b + c * c; MethodCallMonitor.assertionImplementation(MethodCallMonitor.test1_isTriangle_III_V, result == 50, result == 200);
        if(result == 2 * z * z) assert true;
    }
}
