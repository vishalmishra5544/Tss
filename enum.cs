using System;
namespace enum 
{
    class Solution
    {
        enum Days
        {
            Sunday,
            Monday,
            Tuesday,
            Wednesday,
            Thursday,
            Friday,
            Saturday
        }
        static void Main(String [] args)
        {
            Days d1=Days.Sunday;
            Console.WriteLine("first day: "+ d1);
            Days d=Days.Thursday;
            int n=(int) d;
            Console.WriteLine("{0} th day is {1}",n,d);
        }
    }
}