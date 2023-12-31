/*****************************************************************************
 * Project: RooFit                                                           *
 *                                                                           *
 * This code was autogenerated by RooClassFactory                            *
 *****************************************************************************/

// Useful fonctional form to fit quarkonia signal shape

#include "Riostream.h"

#include "NA60Pdf.h"
#include "RooAbsReal.h"
#include "RooAbsCategory.h"
#include <math.h>
#include "TMath.h"

ClassImp(NA60Pdf);

 NA60Pdf::NA60Pdf(const char *name, const char *title,
                        RooAbsReal& _x,
                        RooAbsReal& _xmean,
                        RooAbsReal& _sigma,
	                      RooAbsReal& _alphaleft,
	                      RooAbsReal& _p1left,
                        RooAbsReal& _p2left,
                        RooAbsReal& _p3left,
                        RooAbsReal& _alpharight,
                        RooAbsReal& _p1right,
                        RooAbsReal& _p2right,
                        RooAbsReal& _p3right) :
   RooAbsPdf(name,title),
   x("x","x",this,_x),
   xmean("xmean","xmean",this,_xmean),
   sigma("sigma","sigma",this,_sigma),
   alphaleft("alphaleft","alphaleft",this,_alphaleft),
   p1left("p1left","p1left",this,_p1left),
   p2left("p2left","p2left",this,_p2left),
   p3left("p3left","p3left",this,_p3left),
   alpharight("alpharight","alpharight",this,_alpharight),
   p1right("p1right","p1right",this,_p1right),
   p2right("p2right","p2right",this,_p2right),
   p3right("p3right","p3right",this,_p3right)
 {
 }


 NA60Pdf::NA60Pdf(const NA60Pdf& other, const char* name) :
   RooAbsPdf(other,name),
   x("x",this,other.x),
   xmean("xmean",this,other.xmean),
   sigma("sigma",this,other.sigma),
   alphaleft("alphaleft",this,other.alphaleft),
   p1left("p1left",this,other.p1left),
   p2left("p2left",this,other.p2left),
   p3left("p3left",this,other.p3left),
   alpharight("alpharight",this,other.alpharight),
   p1right("p1right",this,other.p1right),
   p2right("p2right",this,other.p2right),
   p3right("p3right",this,other.p3right)
 {
 }

 Double_t NA60Pdf::evaluate() const
 {
    Double_t t = (x - xmean) / sigma;
    if (sigma < 0){
        t = -t;
    }

    Double_t t0;
    
    if (t >= alpharight){
        double exp = (p2right-p3right * pow(t-alpharight,0.5));
        t0 = 1 + p1right *pow(t-alpharight, exp);
        return TMath::Exp(-0.5 * pow(t/t0,2) );
    }
    
    if (t <= alphaleft){
        double exp = (p2left-p3left * pow(alphaleft-t,0.5));
        t0 = 1 + p1left *pow(alphaleft-t, exp);
        return TMath::Exp(-0.5 * pow((t/t0),2) );
    }
    
   if (alphaleft < t && t < alpharight){
        t0 = 1;
        return TMath::Exp(-0.5 * pow((t/t0),2) );
    }
    
    return 0.;
 }
