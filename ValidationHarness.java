import static org.mockito.Mockito.*;
import org.sosy_lab.sv_benchmarks.Verifier;

public class ValidationHarness {
    public static void main ( String [] args ) {
        mockStatic(Verifier.class);
        
        // The statement is inserted here
        when(Verifier.nondetShort()).thenReturn((short)-25);            
        
        try {
            Short.main(new String[0]);
        } 
        catch (Exception e) {
            System.out.println(e);
        }
    }
}
