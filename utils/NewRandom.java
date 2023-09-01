package utils;

public class NewRandom implements java.io.Serializable{

    private static final long multiplier = 0x5DEECE66DL;
    private static final long addend = 0xBL;
    private static final long mask = (1L << 48) - 1;

    private static final double DOUBLE_UNIT = 0x1.0p-53; // 1.0 / (1L << 53)

//    public Random() {
//        this(seedUniquifier() ^ System.nanoTime());
//    }
//    public Random(long seed) {
//        if (getClass() == Random.class) {
//            long k = initialScramble(seed);
//        }
//        else {
//            // subclass might have overriden setSeed
//            NewAtomicLong newAtomicLong = new NewAtomicLong();
//            setSeed(seed,newAtomicLong);
//        }
//    }
    public static long initialScramble(long seed) {
        return (seed ^ multiplier) & mask;
    }

    public static long seedUniquifier() {
            long current = seedUniquifier.get();
            long next = current * 1181783497276652981L;
            return next;
    }
    public static long createSeed(long timeSeed){
        long seed = timeSeed;
        return seed;
    }
    private static final NewAtomicLong seedUniquifier
            = new NewAtomicLong(8682522807148012L);
    protected int next(int bits,long timeSeed) {
        long oldSeed = initialScramble(seedUniquifier() ^ createSeed(timeSeed));
        long nextSeed = (oldSeed * multiplier + addend) & mask;
        return (int)(nextSeed >>> (48 - bits));
    }

    public int nextInt(long timeSeed) {
        return next(32,timeSeed);
    }
    synchronized public void setSeed(long seed,NewAtomicLong newAtomicLong) {
        newAtomicLong.set(initialScramble(seed));
    }

    public void nextBytes(byte[] bytes,long seed) {
        for (int i = 0, len = bytes.length; i < len; )
            for (int rnd = nextInt(seed),
                 n = Math.min(len - i, Integer.SIZE/Byte.SIZE);
                 n-- > 0; rnd >>= Byte.SIZE)
                bytes[i++] = (byte)rnd;
    }

    public boolean nextBoolean(long seed) {
        return next(1,seed) != 0;
    }

    public long nextLong(long seed) {
        // it's okay that the bottom word remains signed.
        return ((long)(next(32,seed)) << 32) + next(32,seed);
    }

    public float nextFloat(long seed) {
        return next(24,seed) / ((float)(1 << 24));
    }

    public double nextDouble(long seed) {
        return (((long)(next(26,seed)) << 27) + next(27,seed)) * DOUBLE_UNIT;
    }
}
