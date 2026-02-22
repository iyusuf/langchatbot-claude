///usr/bin/env jbang "$0" "$@" ; exit $?
// ^^ Unix shebang trick — makes the file self-executable on Linux/Mac

public class Hello {
    public static void main(String[] args) {
        System.out.println("JBang works.");
    }
}   