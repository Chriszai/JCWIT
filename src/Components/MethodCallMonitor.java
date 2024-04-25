package Components;
import java.lang.reflect.Field;

public class MethodCallMonitor {
    /*
    The method call counter will be presented as a static variable
    * */

    public static int test1_isTriangle_III_V = 0;
    public static int test1_main_LString_V = 0;

    public static void assertionImplementation (int index, boolean ... condition) {
        assert condition[index];
    }
}
