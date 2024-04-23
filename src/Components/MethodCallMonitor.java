package Components;
import java.lang.reflect.Field;

public class MethodCallMonitor {
    /*
    The method call counter will be presented as a static variable
    * */

    public static int Linked_add__I = -1;
    public static int Test_main_LString_V = -1;

    public static void assertionImplementation (String name, boolean ... condition) throws NoSuchFieldException, IllegalAccessException {
        Field field = MethodCallMonitor.class.getDeclaredField(name);
        int value = field.getInt(null);
        assert condition[value];
    }
}
