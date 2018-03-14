#include <iostream>
#include <fstream>
#include <iomanip>
#include <vector>
#include <math.h>

using namespace std;


const float gross_threshold = 0.2F;

int read_gui(const string &filename, vector<string> &gui) {
  gui.clear();
  ifstream is(filename.c_str());
  if (!is.good())
    return -1;

  string s;
  while (is >> s)
    gui.push_back(s);

  return 0;
}

int read_vector(const string &filename, vector<float> &x) {
  x.clear();
  ifstream is(filename.c_str());
  if (!is.good())
    return -1;

  float f;
  while (is >> f)
    x.push_back(f);

  return 0;
}

void compare(const vector<float> &vref, 
	     const vector<float> &vtest, 
	     int &num_voiced, int &num_unvoiced, 
	     int &num_voiced_unvoiced, int &num_unvoiced_voiced, 
	     int &num_voiced_voiced, int &num_gross_errors, 
	     float &fine_error) {
  
  num_voiced = num_unvoiced = num_voiced_unvoiced = num_unvoiced_voiced = 0;
  num_voiced_voiced = num_gross_errors = 0;
  fine_error = 0.0F;
  int nfine = 0;

  if (vref.size() != vtest.size())
      return;

  for (unsigned int i = 0; i < vref.size(); ++i) {

    if (vref[i] == 0.0F)
      num_unvoiced++; 
    else
      num_voiced++;

    if (vref[i] == 0.0F and vtest[i] == 0.0F)
      continue;
  
    if (vref[i] == 0.0F and vtest[i] != 0.0F) {
      num_unvoiced_voiced++;
    } else if (vref[i] != 0.0F and vtest[i] == 0.0F) {
      num_voiced_unvoiced++;
    } else {
      float f = fabs((vref[i] - vtest[i])/vref[i]);
      num_voiced_voiced++;
      if  (f > gross_threshold) {
	num_gross_errors++;
      } else {
	nfine++;
	fine_error += f*f;
      }
    }
  }
  if (nfine > 0)
    fine_error = sqrt(fine_error/nfine);
}

void print_results(int nframes, int num_voiced, int num_unvoiced, int num_voiced_unvoiced, int num_unvoiced_voiced, 
		   int num_voiced_voiced, int num_gross_errors,  float fine_error) {

  cout << "Num. frames:\t" << nframes 
       << " = " << num_unvoiced << " unvoiced + " 
       << num_voiced << " voiced\n";

  cout << "Unvoiced frames as voiced:\t" << num_unvoiced_voiced << "/" << num_unvoiced 
       << " (" << setprecision(2) << 100.0F * num_unvoiced_voiced/num_unvoiced << "%)\n";

  cout << "Voiced frames as unvoiced:\t" << num_voiced_unvoiced << "/" << num_voiced 
       << " (" << 100.0F * num_voiced_unvoiced/num_voiced << "%)\n";

  cout << "Gross voiced errors (+" << 100*gross_threshold << "%):\t" << num_gross_errors << "/" << num_voiced_voiced
       << " (" << 100.0F * num_gross_errors/num_voiced_voiced << "%)\n";
  cout << "MSE of fine errors:\t" << 100*fine_error << "%\n";
}


int main(int argc, const char *argv[]) {
  
  if (argc < 2) {
    cerr << "Usage: " << argv[0] << " file.gui \n";
    cerr << "       For each basename in file.gui, we compare the \n"
         << "       reference pitch values in basename.f0ref \n" 
	 << "       with the obtained values in basename.f0 \n" 
	 << "       Both files has to be in the same directory.";
    return 1;
  }

  int vTot=0, uTot=0, vuTot=0, uvTot=0, nTot=0, grossTot=0, 
    vvTot=0, nfiles=0;
  float fineTot=0.0F;

  vector<string> gui;
  if (read_gui(argv[1], gui)) {
    cerr << "Error reading gui file: " << argv[1] << endl;
    return 1;
  }

  for (int i=0; i<gui.size(); ++i) {
    vector<float> f0ref, f0test;
    string fref = "data/" + gui[i] + ".f0ref";
    if (read_vector(fref, f0ref)) {
      cerr << "Error reading ref file: " << fref << endl;
      return 2;
    }

    string ftest = "data/" + gui[i] + ".f0";
    if (read_vector(ftest, f0test)) {
      cerr << "Error reading test file: " << ftest << endl;
      return 3;
    }
    
    cout << "### Compare " << fref << " and " << ftest << "\n";

    int diff_frames = f0ref.size() - f0test.size();
    if (abs(diff_frames) > 5) {
      cerr << "Error: number of frames in ref (" << f0ref.size() 
	   << ") != number of frames in test (" << f0test.size() 
	   << ")\n";
      return 4;
    } 
    if (diff_frames > 0)      f0ref.resize(f0test.size());
    else if (diff_frames < 0) f0test.resize(f0ref.size());

    int num_voiced, num_unvoiced, num_voiced_unvoiced, num_unvoiced_voiced;
    int num_gross_errors, num_voiced_voiced;
    float fine_error;
    compare(f0ref, f0test, num_voiced, num_unvoiced, 
	    num_voiced_unvoiced, num_unvoiced_voiced, num_voiced_voiced, num_gross_errors, fine_error);    


    vTot     += num_voiced;
    uTot     += num_unvoiced;
    vuTot    += num_voiced_unvoiced;
    uvTot    += num_unvoiced_voiced;

    vvTot    += num_voiced_voiced;
    grossTot += num_gross_errors;
    fineTot  += fine_error;
    nTot     += f0ref.size();
    nfiles++;
    
    print_results(f0ref.size(), num_voiced, num_unvoiced, num_voiced_unvoiced, num_unvoiced_voiced, 
		  num_voiced_voiced, num_gross_errors, fine_error);
    cout << "--------------------------\n\n";
  }   

  if (nfiles > 1) {
    cout << "### Summary\n";
    print_results(nTot, vTot, uTot, vuTot, uvTot, vvTot, grossTot, fineTot/nfiles);
    cout << "--------------------------\n\n";
  }
 
  return 0;  
}
