using System;

namespace var_out_ref
{
    class Helper
    {
        public static void swap(int a,int b)
        {
             int t=a;
             a=b;
             b=t;
        }
        public static void swapRef(ref int a,ref int b)
        {
            int t=a;
            a=b;
            b=a;
        }
        public static void swapOut(out int a,out int b)
        {
             int t=a;
             a=b;
             b=a;
        }
        
    }
    class Solution
    {
        static void Main(String [] args)
        {
           int a=10,b=15;
           Console.WriteLine("Before Swap: a={0} b={1}",a,b);
           Helper.swap(a,b);
           Console.WriteLine("After Swap: a={0} b={1}",a,b);
           Console.WriteLine("Before Swap by ref: a={0} b={1}",a,b);
           Helper.swapRef(ref a,ref b);
           Console.WriteLine("After Swap by ref: a={0} b={1}",a,b);
           Console.WriteLine("Before Swap by out: a={0} b={1}",a,b);
           Helper.swapOut(out a,out b);
           Console.WriteLine("After Swap by out: a={0} b={1}",a,b);
        }
    }
}