# I gotta admit, I do like the minimalism of a Makefile.
# However, I would like it if it had a "watch_file" command:
# 1) Multiple output files for a single rule would look
#    like "too much".
# 2) Needs to be able to keep track of "watch_files" and be
#    able to reference them with a keyword like "$#".
#
#    If either the in files or watch files are newer,
#    then recompile that rule.
#
#```make
#    .WATCH: in_file_1.h
#    out_file: in_file_1.c in_file_two.o
#		gcc -o $@ -c $^
#		echo $#
#```

# Makes the following rules commands.
# E.g. `make clean hello`
.PHONY: clean run compile


# You must specify "main.c helper.o" explicitly
# instead of  referencing the helper rule's
# output_files (Helper::$output_files in Xbt).
a.out: main.c helper.o
	gcc $^ -o $@

helper.o: helper.c helper.h
	# Can't use "$^" here...
	gcc -c helper.c -o $@


# ----- Commands go at the bottom

# Desired Effect: If a.out or some-file.txt
# change and `make run` was passed by the
# user, then execute this rule.
# Issue: This rule always executes when 
#        the user runs `make run`. Would be nice
# 		 to be able to specify a dependency.
# cmd run { 
#   $ xbt compile && xbt run
# }
run: a.out some-file.txt
	make a.out
	$^

compile: main.c helper.o
	make

clean:
	rm *.o a.out