package Components;
import java.lang.reflect.Field;

public class MethodCallMonitor {
    /*
    The method call counter will be presented as a static variable
    * */

    public int Linked_add__I = 0;
    public int Test_main_LString_V = 0;

    public static void assertionImplementation (String name, boolean ... condition){
        try {
            MethodCallMonitor methodMonitor = new MethodCallMonitor();
            Field field = MethodCallMonitor.class.getField(name);
            int value = (int) field.get(methodMonitor);
        } catch (NoSuchFieldException e) {
            throw new RuntimeException(e);
        } catch (IllegalAccessException e) {
            throw new RuntimeException(e);
        }
    }
}
