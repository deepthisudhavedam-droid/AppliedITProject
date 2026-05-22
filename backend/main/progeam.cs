using MyOutletApp.Models;
using MyOutletApp.Services;
using MyOutletApp.Utils;

class Program
{
    static void Main(string[] args)
    {
        OutletService service = new OutletService();

        while (true)
        {
            Console.WriteLine("\n==== OUTLET MANAGEMENT SYSTEM ====");
            Console.WriteLine("1. Add Outlet");
            Console.WriteLine("2. View All Outlets");
            Console.WriteLine("3. Delete Outlet");
            Console.WriteLine("4. Exit");
            Console.Write("Select option: ");

            var input = Console.ReadLine();

            switch (input)
            {
                case "1":
                    AddOutlet(service);
                    break;

                case "2":
                    service.GetAllOutlets();
                    break;

                case "3":
                    DeleteOutlet(service);
                    break;

                case "4":
                    return;

                default:
                    Logger.Error("Invalid option!");
                    break;
            }
        }
    }

    static void AddOutlet(OutletService service)
    {
        Console.Write("Enter Id: ");
        int id = int.Parse(Console.ReadLine());

        Console.Write("Enter Name: ");
        string name = Console.ReadLine();

        Console.Write("Enter Location: ");
        string location = Console.ReadLine();

        service.AddOutlet(new Outlet
        {
            Id = id,
            Name = name,
            Location = location
        });

        Logger.Info("Outlet added successfully!");
    }

    static void DeleteOutlet(OutletService service)
    {
        Console.Write("Enter Id to delete: ");
        int id = int.Parse(Console.ReadLine());

        service.DeleteOutlet(id);
        Logger.Info("Outlet deleted (if existed).");
    }
}
``