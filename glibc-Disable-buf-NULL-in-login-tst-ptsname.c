Author: Arjun Shankar <arjun.is@lostca.se>
Date:   Wed May 31 14:09:46 2017 +0200

    Disable buf=NULL in login/tst-ptsname.c

Index: b/login/tst-ptsname.c
===================================================================
--- a/login/tst-ptsname.c
+++ b/login/tst-ptsname.c
@@ -70,7 +70,6 @@ do_test (void)
   if (fd != -1)
     {
       result |= do_single_test (fd, buf, sizeof (buf), 0);
-      result |= do_single_test (fd, NULL, sizeof (buf), EINVAL);
       result |= do_single_test (fd, buf, 1, ERANGE);
       close (fd);
     }
