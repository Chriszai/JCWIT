import static java.lang.Math.max;

public class test1 {
    public static void main(String[] args) {
        isTriangle(3,4,5);
    }
    static boolean isTriangle(int a, int b, int c){
        int z = max(a,b);
        assert z == 5;
        z = max(z,c);
        int result = a ^ 2 + b ^ 2 + c ^ 2;
        if(result == 2 * (z ^ 2)) return true;
        return false;
    }
}
