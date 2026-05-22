using MyOutletApp.Models;

namespace MyOutletApp.Services
{
    public class OutletService
    {
        private List<Outlet> _outlets = new List<Outlet>();

        public void AddOutlet(Outlet outlet)
        {
            _outlets.Add(outlet);
        }

        public void GetAllOutlets()
        {
            foreach (var outlet in _outlets)
            {
                outlet.Display();
            }
        }

        public Outlet GetById(int id)
        {
            return _outlets.FirstOrDefault(o => o.Id == id);
        }

        public void DeleteOutlet(int id)
        {
            var outlet = GetById(id);
            if (outlet != null)
            {
                _outlets.Remove(outlet);
            }
        }
    }
}
