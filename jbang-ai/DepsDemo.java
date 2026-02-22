///usr/bin/env jbang "$0" "$@" ; exit $?
//DEPS com.google.guava:guava:32.1.3-jre
//DEPS org.slf4j:slf4j-simple:2.0.9

import com.google.common.collect.ImmutableList;

public class DepsDemo {
    public static void main(String[] args) {
        // ImmutableList is a Guava type — pulled from Maven Central automatically
        var items = ImmutableList.of("alpha", "beta", "gamma");
        items.forEach(System.out::println);
    }
}