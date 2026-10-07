def Na_calc(self, ma, zacc, Mhost, z0=0.0, N_herm=200, Nrand=1000, Na_model=3):
    """Evaluate the Yang et al. accretion rate with ITAMAE quadrature.

    Parameters
    ----------
    ma : numpy.ndarray
        Accretion-mass grid. A two-dimensional input must have redshift as
        its leading axis, matching the legacy implementation.
    zacc : numpy.ndarray
        Accretion-redshift grid.
    Mhost : float
        Host mass at ``z0`` in legacy solar-mass units.
    z0 : float, optional
        Host reference redshift.
    N_herm : int, optional
        Gauss-Hermite order for host-history scatter.
    Nrand : int, optional
        Resolution of the auxiliary redshift inversion grid.
    Na_model : {1, 2, 3}, optional
        Yang et al. normalization variant.

    Returns
    -------
    numpy.ndarray
        Differential accretion abundance with shape ``(len(zacc), len(ma))``.
    """

    zacc_2d = np.asarray(zacc).reshape(-1, 1)
    M200_0 = self.Mzzi(Mhost, zacc_2d, z0)
    sigmalogM200 = 0.12 - 0.15 * np.log10(M200_0 / Mhost)
    M200, host_weight = gauss_hermite_lognormal(M200_0, sigmalogM200, order=N_herm)

    mmax = np.minimum(M200, Mhost / 2.0)
    Mmax = np.minimum(M200_0 + mmax, Mhost)

    if Na_model == 3:
        zlist = zacc_2d * np.linspace(1.0, 0.0, Nrand)
        iMmax = np.argmin(np.abs(self.Mzzi(Mhost, zlist, z0) - Mmax), axis=-1)
        z_Max = zlist[np.arange(len(zlist)), iMmax]
        z_Max_3d = z_Max.reshape(N_herm, len(zlist), 1)
        delcM = self.deltac_func(z_Max_3d)
        delca = self.deltac_func(zacc_2d)
        sM = self.s_func(Mmax)
        sa = self.s_func(ma)
        xmax = (delca - delcM) ** 2 / (2.0 * (self.s_func(mmax) - sM))
        normB = special.gamma(0.5) * special.gammainc(0.5, xmax) / np.sqrt(np.pi)
        Phi = (
            self.Ffunc_Yang(delcM, delca, sM, sa)
            / normB
            * np.heaviside(mmax - ma, 0)
        )
    elif Na_model == 1:
        delca = self.deltac_func(zacc_2d)
        sM = self.s_func(M200)
        sa = self.s_func(ma)
        xmin = self.s_func(mmax) - self.s_func(M200)
        normB = (
            1.0
            / np.sqrt(2.0 * np.pi)
            * delca
            * 2.0
            / xmin**0.5
            * special.hyp2f1(0.5, 0.0, 1.5, -sM / xmin)
        )
        Phi = self.Ffunc(delca, sM, sa) / normB * np.heaviside(mmax - ma, 0)
    elif Na_model == 2:
        delca = self.deltac_func(zacc_2d)
        sM = self.s_func(M200)
        sa = self.s_func(ma)
        xmin = self.s_func(mmax) - self.s_func(M200)
        normB = (
            1.0
            / np.sqrt(2.0 * np.pi)
            * delca
            * 0.57
            * (delca / np.sqrt(sM)) ** -0.01
            * (2.0 / (1.0 - 0.38))
            * sM ** (-0.38 / 2.0)
            * xmin ** (0.5 * (0.38 - 1.0))
            * special.hyp2f1(
                0.5 * (1.0 - 0.38),
                -0.38 / 2.0,
                0.5 * (3.0 - 0.38),
                -sM / xmin,
            )
        )
        Phi = (
            self.Ffunc(delca, sM, sa)
            * self.Gfunc(delca, sM, sa)
            / normB
            * np.heaviside(mmax - ma, 0)
        )
    else:
        raise ValueError("Na_model must be 1, 2, or 3.")

    F2 = np.sum(np.nan_to_num(Phi) * host_weight, axis=0)
    return F2 * self.dsdm(ma, 0.0) * self.dMdz(Mhost, zacc_2d, z0) * (1.0 + zacc_2d)
