using System;
using System.Collections;
namespace String_Builder
{
    class Solution
    {
        static void Main(string [] args)
        {
            String str="Vishal";
            StringBuilder s=new StringBuilder(str);
            s.Append("Mishra");
            Console.WriteLine("After Append(\"Mishra\") :");
            Console.WriteLine(s);
            s.Insert(6," ");
            Console.WriteLine("After Insert(6,\" \") :");
            Console.WriteLine(s);
            s.Remove(6,1);
            Console.WriteLine("After Remove(6,1) :");
            Console.WriteLine(s);
            s.Replace("Vishal","Mr.");
            Console.WriteLine("After Replace(\"Vishal\",\"Mr.\") :");            
            Console.WriteLine(s);
        }
    }
}