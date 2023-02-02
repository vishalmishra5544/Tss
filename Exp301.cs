using System;
using System.Collections.Generic;
namespace Exp301
{
 class Helper
 {
  public static void sort(List<String> l)
  {
    for(int i=0;i<l.Count-1;i++)
    {
      for(int j=0;j<l.Count-1;j++)
      {
        if(l[j].CompareTo(l[j+1])>0)
        {
           String t=l[j];
           l[j]=l[j+1];
           l[j+1]=t;
        }
      }
    }
  }
 }
 class Program
 {
   static void Main(String [] args)
   {
     List<String> l=new List<String>();
     Console.WriteLine("Enter no of strings:");
     int n=Convert.ToInt32(Console.ReadLine());
     Console.WriteLine("Enter {0} strings:");
     for(int i=0;i<n;i++)
     {
       l.Add(Console.ReadLine());
     }
     Helper.sort(l);
     Console.WriteLine("Sorted list by alphabetical order!!");
     for(String s in l)
     {
       Console.Write(s+" ");
     }
   }
 }
}