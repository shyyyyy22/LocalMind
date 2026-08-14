import java.io.File;
import java.util.Arrays;

/**
 * Main.java - a tiny Java program that walks a directory tree.
 * Used as test input for the LocalMind code parser.
 */
public class Main {

    public static void main(String[] args) {
        File root = new File("D:/Test");
        System.out.println("Scanning: " + root.getAbsolutePath());
        listFiles(root, 0);
    }

    private static void listFiles(File dir, int depth) {
        File[] children = dir.listFiles();
        if (children == null) {
            return;
        }
        Arrays.sort(children);
        for (File child : children) {
            String indent = "  ".repeat(depth);
            if (child.isDirectory()) {
                System.out.println(indent + "[DIR] " + child.getName());
                listFiles(child, depth + 1);
            } else {
                System.out.println(indent + "[FILE] " + child.getName() + " (" + child.length() + " bytes)");
            }
        }
    }
}
