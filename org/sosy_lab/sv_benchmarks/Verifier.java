package org.sosy_lab.sv_benchmarks;

import java.util.Random;

public final class Verifier {
  public static void assume(boolean condition) {
    if (!condition) {
      Runtime.getRuntime().halt(1);
    }
  }

  public static boolean nondetBoolean() {
    return new Random().nextBoolean();
  }

  public static byte nondetByte() {
    return (byte) (new Random().nextInt());
  }

  public static char nondetChar() {
    return (char) (new Random().nextInt());
  }

  public static short nondetShort() {
    return (short) (new Random().nextInt());
  }

  public static int nondetInt() {
    return new Random().nextInt();
  }

  public static long nondetLong() {
    return new Random().nextLong();
  }

  public static float nondetFloat() {
    return new Random().nextFloat();
  }

  public static double nondetDouble() {
    return new Random().nextDouble();
  }

  public static String nondetString() {
    Random random = new Random();
    int size = random.nextInt();
    assume(size >= 0);
    byte[] bytes = new byte[size];
    random.nextBytes(bytes);
    return new String(bytes);
  }
}