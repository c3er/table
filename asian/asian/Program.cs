using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Windows.Forms;
using System.Threading;

namespace ConsoleApplication1
{
    class MtValues
    {
        private bool _completed = false;
        private string _result = null;

        private Mutex _completedMutex = null;
        private Mutex _resultMutex = null;

        public MtValues()
        {
            _completedMutex = new Mutex();
            _resultMutex = new Mutex();
        }

        public bool Completed
        {
            get
            {
                _completedMutex.WaitOne();
                bool completed = _completed;
                _completedMutex.ReleaseMutex();
                return completed;
            }
            set
            {
                _completedMutex.WaitOne();
                _completed = value;
                _completedMutex.ReleaseMutex();
            }
        }

        public string Result
        {
            get
            {
                _resultMutex.WaitOne();
                string result = _result;
                _resultMutex.ReleaseMutex();
                return result;
            }
            set
            {
                _resultMutex.WaitOne();
                _result = value;
                _resultMutex.ReleaseMutex();
            }
        }
    }

    class Program
    {
        static MtValues values = new MtValues();

        static void wb_DocumentCompleted(object sender, WebBrowserDocumentCompletedEventArgs e)
        {
            WebBrowser wb = (WebBrowser)sender;
            values.Result = wb.Document.Body.OuterHtml;
            values.Completed = true;
        }

        [STAThreadAttribute]
        static int Main(string[] args)
        {
            if (args.Length == 0)
            {
                Console.WriteLine("Bitte Webseite angeben");
                return 1;
            }
            string addr = args[0];
            WebBrowser wb = new WebBrowser();
            wb.DocumentCompleted += new WebBrowserDocumentCompletedEventHandler(wb_DocumentCompleted);
            wb.Navigate(new Uri(addr));
            while (!values.Completed)
            {
                Application.DoEvents();
                Thread.Sleep(50);
            }
            Console.Write(values.Result);
            wb.Dispose();
            return 0;
        }
    }
}
