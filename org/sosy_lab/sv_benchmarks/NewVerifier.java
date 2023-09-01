package org.sosy_lab.sv_benchmarks;

import utils.NewRandom;


public final class NewVerifier implements java.io.Serializable {
    public static void assume(boolean condition) {
        if (!condition) {
            Runtime.getRuntime().halt(1);
        }
    }

    public boolean nondetBoolean(long seed) {
        return new NewRandom().nextBoolean(seed);
    }

    public byte nondetByte(long seed) {
        return (byte) (new NewRandom().nextInt(seed));
    }

    public char nondetChar(long seed) {
        return (char) (new NewRandom().nextInt(seed));
    }

    public short nondetShort(long seed) {
        return (short) (new NewRandom().nextInt(seed));
    }

    public int nondetInt(long seed) {
        return new NewRandom().nextInt(seed);
    }

    public long nondetLong(long seed) {
        return new NewRandom().nextLong(seed);
    }

    public float nondetFloat(long seed) {
        return new NewRandom().nextFloat(seed);
    }

    public double nondetDouble(long seed) {
        return new NewRandom().nextDouble(seed);
    }

    public String nondetString(long seed) {
        NewRandom random = new NewRandom();
        int size = random.nextInt(seed);
        assume(size >= 0);
        byte[] bytes = new byte[size];
        random.nextBytes(bytes,seed);
        return new String(bytes);
    }
}
