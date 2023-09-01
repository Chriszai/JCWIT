package utils;

public class test {
    public static void main(String[]args){
        recursion(8);

        assert false;
    }
    
    public static void recursion(int i){
        if(i<=0){
            assert false;
        }
        if(i>0){
            recursion(i-1);
        }
    }
}
