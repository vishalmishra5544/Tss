using System;
namespace foreach 
{
    class Solution
    {
        static void Main(String [] args)
        {
            List<int> l=new List<int>();
            l.Add(1);
            l.Add(11);
            l.Add(111);
            Console.WriteLine("using foreach loop Elements of l:");
            foreach(int ele in l)
            {
                Console.Write(ele+" ");
            }
            Console.WriteLine("using l.ForEach() method Elements of l:");
            l.ForEach(ele=>{Console.Write(ele+" ");});
           
        }
    }
}
