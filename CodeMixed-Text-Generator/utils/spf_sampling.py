import math
from .rcm_std_mean import switchpoint_u

def create_pdf(x, mean, std):
    '''
    PDF value of a normal distribution from mean and std of SPF of the RCM input corpus
    '''
    var = float(std)**2
    denom = (2*math.pi*var)**.5
    num = math.exp(-(float(x)-float(mean))**2/(2*var))
    return num/denom

def rank(gcm, langtags, spf_mean, spf_std):
    gcm_probs = []
    processed_gcm = []

    # convert gcm to the format which switchpoint_u expects (3d array)
    for cm, _ in gcm:
        t = cm.split()
        tmp = []
        for w in t:
            tmp.append(w.split('/'))
        processed_gcm.append(tmp)

    # generate probs
    for cm_p, cm_row in zip(processed_gcm, gcm):
        cm, cm_tree = cm_row
        spf = switchpoint_u(cm_p, langtags)
        prob = create_pdf(spf, spf_mean, spf_std)
        gcm_probs.append((cm, cm_tree, prob))

    # sort sentences based on prob
    gcm_probs = sorted(gcm_probs, key=lambda x: x[2], reverse=True)

    # return output
    output = [(x[0], x[1]) for x in gcm_probs] 

    return output