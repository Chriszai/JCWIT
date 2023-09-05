import static org.mockito.Mockito.*;
import org.sosy_lab.sv_benchmarks.Verifier;

public class ValidationHarness {
    public static void main ( String [] args ) {
        mockStatic(Verifier.class);
        
        // The statement is inserted here
        when(Verifier.Type()).thenReturn(true);            
        
        StringValueOf04.main(new String [0]);
    }
}
